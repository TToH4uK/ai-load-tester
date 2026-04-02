import httpx
import time
from typing import Dict, Any

class HTTPBotClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url
        self.timeout = timeout

    async def send_message(self, text: str) -> Dict[str, Any]:
        """
        Отправляет сообщение боту и замеряет метрики.
        """
        start_time = time.perf_counter()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}",
                    json={"text": text}
                )
                response.raise_for_status()
                
                latency = time.perf_counter() - start_time
                
                return {
                    "status": "success",
                    "text": response.json().get("text", ""),
                    "latency": latency,
                    "status_code": response.status_code
                }
        except Exception as e:
            latency = time.perf_counter() - start_time
            return {
                "status": "error",
                "error_message": str(e),
                "latency": latency,
                "status_code": 0
            }