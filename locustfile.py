import uuid
from locust import HttpUser, task, between

class BankUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.session_id = f"test_{uuid.uuid4().hex[:8]}"
        self.headers = {
            "Content-Type": "application/json",
            "X-Session-ID": self.session_id
        }

    @task
    def dialog_flow(self):
        scenario_steps = [
            {"text": "Hello, good morning", "expected": "start"},
            {"text": "I want to apply for a loan", "expected": "credit_init"},
            {"text": "personal loan", "expected": "loan_check_history"},
            {"text": "no delays", "expected": "loan_info"},
            {"text": "less than a million", "expected": "loan_insurance"}
        ]

        for step in scenario_steps:
            current_headers = self.headers.copy()
            current_headers["X-Expected-Intent"] = step["expected"]

            with self.client.post(
                "/chat", 
                json={"text": step["text"]}, 
                headers=current_headers, 
                catch_response=True
            ) as resp:
                if resp.status_code == 200:
                    resp.success()
                else:
                    resp.failure(f"Server error: {resp.status_code}")

        self.on_start()

    @task(1)
    def test_unknown_phrases(self):
        current_headers = self.headers.copy()
        current_headers["X-Expected-Intent"] = "unknown" 
        
        self.client.post(
            "/chat", 
            json={"text": "How can I patch KDE under FreeBSD?"}, 
            headers=current_headers
        )