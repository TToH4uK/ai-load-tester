import random
import yaml
import logging
import os
from locust import HttpUser, task, constant, events
from locust.exception import StopUser

# 1. Logging Configuration (minimal to avoid console spam)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Scenario Path (from env or default)
SCENARIO_PATH = os.getenv("SCENARIO_PATH", "scenarios/example.yaml")

# Global variable to store steps (loaded once on worker start)
SCENARIO_STEPS = []

def load_scenario():
    global SCENARIO_STEPS
    try:
        with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            # Extract only the list of questions (user_say)
            SCENARIO_STEPS = [step.get("user_say") for step in config_data.get("steps", [])]
        logger.info(f"✅ [Worker {os.getpid()}] Scenario loaded: {len(SCENARIO_STEPS)} steps.")
    except Exception as e:
        logger.error(f"❌ Error loading scenario: {e}")
        SCENARIO_STEPS = ["How to open an account?"] # Fallback to avoid crash

load_scenario()

class BankBotUser(HttpUser):
    # Loop without pauses to find maximum RPS. 
    # To imitate real humans, change to between(1, 2)
    wait_time = constant(0) 

    @task
    def ask_question(self):
        # Pick a random block of questions from the scenario
        user_phrases = random.choice(SCENARIO_STEPS)
        
        # If it's a list - pick one random, if it's a string - use it directly
        question = random.choice(user_phrases) if isinstance(user_phrases, list) else user_phrases

        # Send primitive GET request
        # catch_response=True is not used if we don't do complex body validation
        with self.client.get("/ask", params={"q": question}, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Fail: {response.status_code}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    if not hasattr(environment.runner, 'master_id'):
        logger.info("📊 Тест завершен. Проверьте вкладку Statistics.")