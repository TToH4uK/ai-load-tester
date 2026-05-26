import asyncio
import random
from core.protocols.http_protocol import HTTPBotClient
from scenarios.models import Scenario
from brain.validator import SemanticValidator

class VirtualUser:
    def __init__(self, user_id: int, scenario: Scenario, base_url: str, validator: SemanticValidator, stats):
        self.user_id = user_id
        self.scenario = scenario
        self.steps_map = {step.id: step for step in scenario.steps}
        
        self.client = HTTPBotClient(base_url, timeout=scenario.config.timeout)
        self.validator = validator
        self.stats = stats 
        
        self.persona = random.choice(["standard", "hurried", "detailed"])
        self.delay_mult = {"standard": 1.0, "hurried": 0.5, "detailed": 2.0}[self.persona]
        
        self.current_step_id = scenario.steps[0].id if scenario.steps else "end"
        self.is_active = True

    async def run(self):
        print(f"👤 [User {self.user_id} | {self.persona}] В игре")

        while self.is_active:
            step = self.steps_map.get(self.current_step_id)
            if not step or self.current_step_id == "end":
                break

            text_to_send = step.user_say
            if isinstance(text_to_send, list):
                text_to_send = random.choice(text_to_send)

            base_delay = random.randint(*self.scenario.config.typing_delay)
            await asyncio.sleep(base_delay * self.delay_mult)

            result = await self.client.send_message(text_to_send)

            score = 0.0
            if result["status"] == "success":
                bot_text = result.get("text", "")
                is_valid = False
                rules = getattr(step, 'validation', None)
                
                if rules:
                    if rules.contains:
                        for substring in rules.contains:
                            if substring.lower() in bot_text.lower():
                                is_valid = True
                                score = 1.0
                                break
                    elif rules.intent or text_to_send:
                        target = rules.intent if rules.intent else text_to_send
                        score = self.validator.get_similarity(bot_text, target)
                        min_sim = rules.min_similarity if rules.min_similarity is not None else 0.7
                        is_valid = score >= min_sim
                    else:
                        is_valid = True
                else:
                    is_valid = True

                if is_valid:
                    print(f"✅ [User {self.user_id}] OK! (Score: {score:.2f})")
                    self.current_step_id = step.on_success
                else:
                    print(f"⚠️ [User {self.user_id}] Low Score: {score:.2f}")
                    self.current_step_id = step.on_fail
            else:
                print(f"❌ [User {self.user_id}] Ошибка сети")
                self.is_active = False

            self.stats.add_metric(result.get("latency", 0), score, result["status"])

        self.is_active = False