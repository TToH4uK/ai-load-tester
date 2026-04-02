import random
import yaml
import logging
import gevent
import os
from locust import HttpUser, task, between, events
from locust.exception import StopUser

from scenarios.models import Scenario
from brain.validator import SemanticValidator

# 1. Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Глобальный валидатор
VALIDATOR = SemanticValidator()

SCENARIO_PATH = os.getenv("SCENARIO_PATH", "scenarios/example.yaml")

try:
    with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
        SCENARIO = Scenario(**config_data)
        STEPS_MAP = {step.id: step for step in SCENARIO.steps}
    logger.info(f"✅ [Worker {os.getpid()}] Сценарий '{SCENARIO.name}' загружен.")
except Exception as e:
    logger.error(f"❌ Ошибка загрузки сценария: {e}")
    raise e

class BankBotUser(HttpUser):
    wait_time = between(2, 4)

    def on_start(self):
        """Инициализация пользователя"""
        if not SCENARIO.steps:
            raise StopUser("Сценарий пуст")
        
        self.current_step_id = SCENARIO.steps[0].id
        
        # --- ИСПРАВЛЕНИЕ: Добавляем атрибуты, которых не хватало ---
        self.persona = random.choice(["hurried", "standard", "detailed"])
        # Привязываем множитель задержки к персоне
        self.delay_mult = {
            "hurried": 0.7, 
            "standard": 1.0, 
            "detailed": 1.4
        }[self.persona]
        # --------------------------------------------------------

    @task
    def conversation_flow(self):
        # Если дошли до конца или ID невалиден - сбрасываем на начало
        if self.current_step_id == "end" or self.current_step_id not in STEPS_MAP:
            self.current_step_id = SCENARIO.steps[0].id
            logger.info(f"🔄 Пользователь {self.persona} начинает сценарий заново")
            return

        step = STEPS_MAP[self.current_step_id]
        text_to_send = random.choice(step.user_say) if isinstance(step.user_say, list) else step.user_say

        # Имитация "времени на раздумья" с учетом персоны
        gevent.sleep(self.wait_time() * self.delay_mult)

        params = {"q": text_to_send}
        
        with self.client.get("/ask", params=params, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    bot_text = data.get("answer", "")
                    source = data.get("source", "unknown")
                    
                    target = step.validation.intent if (step.validation and step.validation.intent) else text_to_send
                    score = VALIDATOR.get_similarity(bot_text, target)
                    threshold = step.validation.min_similarity if step.validation else 0.7
                    
                    if score >= threshold:
                        response.success()
                        self.current_step_id = step.on_success
                    else:
                        response.failure(f"Low AI Score: {score:.2f} | Source: {source}")
                        self.current_step_id = step.on_fail
                        
                except Exception as e:
                    response.failure(f"JSON Error: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    if not hasattr(environment.runner, 'master_id'):
        logger.info("📊 Тест завершен.")