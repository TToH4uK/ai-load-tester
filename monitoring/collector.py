import threading

class StatsCollector:
    def __init__(self):
        self.metrics = []
        self._lock = threading.Lock()

    def add_metric(self, latency: float, score: float, status: str):
        with self._lock:
            self.metrics.append({
                "latency": latency,
                "score": score,
                "status": status
            })

    def print_report(self):
        print("\n" + "="*40)
        print("📊 ИТОГОВЫЙ ОТЧЕТ НАГРУЗОЧНОГО ТЕСТА")
        print("="*40)
        
        total = len(self.metrics)
        if total == 0:
            print("Нет собранных метрик.")
            return
            
        successes = sum(1 for m in self.metrics if m["status"] == "success")
        errors = total - successes
        avg_latency = sum(m["latency"] for m in self.metrics) / total
        avg_score = sum(m["score"] for m in self.metrics) / total
        
        print(f"Всего запросов:  {total}")
        print(f"Успешных:        {successes}")
        print(f"Ошибок:          {errors}")
        print(f"Ср. время (сек): {avg_latency:.2f}")
        print(f"Ср. скор (AI):   {avg_score:.2f}")
        print("="*40)
