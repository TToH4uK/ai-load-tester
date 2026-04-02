import random
import yaml
import logging
import gevent
from concurrent.futures import ThreadPoolExecutor
from locust import HttpUser, task, between, events
from locust.exception import StopUser

from scenarios.models import Scenario
from brain.validator import SemanticValidator

# 1. Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Глобальные ресурсы (создаются один раз при старте)
# Пул потоков, чтобы нейросеть не вешала CPU основного процесса
executor = ThreadPoolExecutor(max_workers=20)
VALIDATOR = SemanticValidator()

# Загрузка сценария
try:
    with open("scenarios/example.yaml", "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
        SCENARIO = Scenario(**config_data)
        STEPS_MAP = {step.id: step for step in SCENARIO.steps}
    logger.info(f"✅ Сценарий '{SCENARIO.name}' загружен. Шагов: {len(STEPS_MAP)}")
except Exception as e:
    logger.error(f"❌ Ошибка загрузки сценария: {e}")
    raise e

class BankBotUser(HttpUser):
    # Берем задержку из конфигурации YAML
    wait_time = between(3, 5)

    def on_start(self):
        """Вызывается при старте каждого виртуального пользователя"""
        if not SCENARIO.steps:
            raise StopUser("Сценарий пуст")
        self.current_step_id = SCENARIO.steps[0].id
        # Разные типы пользователей для реалистичности
        self.persona = random.choice(["hurried", "standard", "detailed"])
        self.delay_mult = {"hurried": 0.5, "standard": 1.0, "detailed": 1.5}[self.persona]

    @task
    def chat_workflow(self):
        if self.current_step_id == "end" or self.current_step_id not in STEPS_MAP:
            raise StopUser()

        step = STEPS_MAP[self.current_step_id]
        
        # Выбор фразы пользователя
        text_to_send = random.choice(step.user_say) if isinstance(step.user_say, list) else step.user_say

        # Имитация набора текста (не блокирует поток благодаря gevent)
        extra_wait = self.wait_time() * (self.delay_mult - 1)
        if extra_wait > 0:
            gevent.sleep(extra_wait)

        payload = {"text": text_to_send}
        
        # Основной запрос к боту
        with self.client.post("/chat", json=payload, catch_response=True, timeout=SCENARIO.config.timeout) as response:
            if response.status_code == 200:
                try:
                    bot_response = response.json()
                    bot_text = bot_response.get("text", "")
                    
                    # Определение цели для сравнения
                    target = step.validation.intent if (step.validation and step.validation.intent) else text_to_send
                    
                    # 3. МАГИЯ ОПТИМИЗАЦИИ: Вычисляем семантику в пуле потоков
                    # Это позволяет Locust продолжать работу, пока CPU считает вектор
                    future = executor.submit(VALIDATOR.get_similarity, bot_text, target)
                    score = future.result() # Получаем результат
                    
                    threshold = step.validation.min_similarity if step.validation else 0.7
                    
                    if score >= threshold:
                        response.success()
                        self.current_step_id = step.on_success
                    else:
                        response.failure(f"AI Score Low: {score:.2f} (Target: {target[:20]}...)")
                        self.current_step_id = step.on_fail
                        
                except Exception as e:
                    response.failure(f"Parsing Error: {str(e)}")
                    self.current_step_id = "end"
            else:
                response.failure(f"HTTP {response.status_code}: {response.text[:50]}")
                self.current_step_id = "end"

# 4. Обработчик завершения теста (сохранение отчета)
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    try:
        stats = environment.stats
        filename = "final_report.csv"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Name,Requests,Failures,Avg Response Time,Min,Max\n")
            # Проходим по всем эндпоинтам
            for entry in stats.entries.values():
                f.write(f"{entry.name},{entry.num_requests},{entry.num_failures},"
                        f"{entry.avg_response_time:.2f},{entry.min_response_time:.2f},"
                        f"{entry.max_response_time:.2f}\n")
        logger.info(f"📊 Итоговый отчет сохранен в {filename}")
    except Exception as e:
        logger.error(f"❌ Не удалось сохранить отчет: {e}")

# 5. Очистка ресурсов при выходе
@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    executor.shutdown(wait=False)