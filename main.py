import sys
import os
import asyncio
import yaml

# Добавляем корень проекта в пути поиска модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scenarios.models import Scenario
from core.virtual_user import VirtualUser
from brain.validator import SemanticValidator
from monitoring.collector import StatsCollector

async def run_load_test(scenario_path: str, user_count: int):
    # 1. Загружаем сценарий
    with open(scenario_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    scenario = Scenario(**config_data)
    
    # ПРИОРИТЕТ: берем URL из переменной окружения (для Docker), 
    # если её нет — из YAML (для локального запуска)
    target_url = os.getenv("TARGET_URL", scenario.config.base_url)
    
    print(f"🚀 Запуск теста: {scenario.name}")
    print(f"🧠 Инициализация нейропрофиля...")
    
    shared_validator = SemanticValidator()
    stats = StatsCollector()
    
    print(f"👥 Создание {user_count} виртуальных пользователей...")
    print(f"🎯 Целевой URL: {target_url}")
    print("-" * 30)

    tasks = []
    for i in range(user_count):
        user = VirtualUser(
            user_id=i, 
            scenario=scenario, 
            base_url=target_url, 
            validator=shared_validator,
            stats=stats
        )
        tasks.append(user.run())

    await asyncio.gather(*tasks)
    
    # Вывод финального отчета
    stats.print_report()

if __name__ == "__main__":
    # Можно переопределить путь к сценарию через ENV
    SCENARIO_FILE = os.getenv("SCENARIO_PATH", "scenarios/example.yaml")
    USER_LOAD = int(os.getenv("USER_COUNT", 20))
    
    try:
        asyncio.run(run_load_test(SCENARIO_FILE, USER_LOAD))
    except KeyboardInterrupt:
        print("\n🛑 Тест прерван")