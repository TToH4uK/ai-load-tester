import uuid
from locust import HttpUser, task, between

class BankUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # Генерируем сессию
        self.session_id = f"test_{uuid.uuid4().hex[:8]}"
        self.headers = {
            "Content-Type": "application/json",
            "X-Session-ID": self.session_id
        }

    @task
    def dialog_flow(self):
        # Список фраз, которые ТАКЖЕ должны быть в твоем YAML
        messages = [
            "Привет!",
            "Я хочу взять кредит",
            "нет",
            "500000"
        ]

        for msg in messages:
            # Используем catch_response=True, чтобы самим решать, что ошибка, а что нет
            with self.client.post("/chat", json={"text": msg}, headers=self.headers, catch_response=True) as resp:
                if resp.status_code == 200:
                    # Если сервер ответил 200 — это уже успех для сетевого теста
                    resp.success()
                else:
                    # Ошибка, только если сервер реально "упал" (500, 404 и т.д.)
                    resp.failure(f"Server returned {resp.status_code}")

        # Важно: сбрасываем сессию, чтобы бот начал с начала (шаг 'start')
        self.on_start()