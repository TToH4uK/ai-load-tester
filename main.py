import sys
import os
import asyncio
import yaml
import time
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session

# Добавляем корень проекта в пути поиска модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_manager.session import init_db, SessionLocal
from db_manager.models import FAQ
from brain.validator import SemanticValidator

app = FastAPI(title="Bank AI Bot")

# Глобальный валидатор, чтобы не грузить его на каждый запрос
VALIDATOR = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    global VALIDATOR
    
    print("🗄️  Подключение к PostgreSQL...")
    # Цикл ожидания базы (Retry logic)
    for i in range(10):
        try:
            init_db()
            with SessionLocal() as db:
                if db.query(FAQ).count() == 0:
                    print("📝 Наполнение базы данными...")
                    db.add_all([
                        FAQ(question="Как открыть счет?", answer="В приложении или отделении с паспортом."),
                        FAQ(question="Лимит по карте", answer="Стандартный лимит — 500 000 руб. в сутки."),
                        FAQ(question="Где мой кешбэк?", answer="Начисляется 10-го числа каждого месяца.")
                    ])
                    db.commit()
            print("✅ База данных готова.")
            break
        except Exception as e:
            print(f"🔄 Попытка {i+1}: База еще не доступна, ждем... ({e})")
            time.sleep(3)
    else:
        print("❌ Не удалось подключиться к БД.")

    print("🔥 Прогрев нейросети...")
    VALIDATOR = SemanticValidator()
    VALIDATOR.get_similarity("проверка", "тест")
    print("✅ Система готова к работе.")

@app.get("/ask")
async def ask_bot(q: str = Query(...), db: Session = Depends(get_db)):
    """Основной эндпоинт, куда стучит Locust"""
    # 1. Сначала ищем в базе точное совпадение
    result = db.query(FAQ).filter(FAQ.question == q).first()
    
    if result:
        return {"answer": result.answer, "source": "postgres"}
    
    # 2. Если нет в базе — отдаем дефолт (тут можно прикрутить LLM)
    return {"answer": "К сожалению, я не нашел точного ответа в базе.", "source": "fallback"}

@app.post("/chat")
async def chat_endpoint(payload: dict, db: Session = Depends(get_db)):
    """Альтернативный эндпоинт для POST запросов"""
    text = payload.get("text", "")
    return await ask_bot(q=text, db=db)

if __name__ == "__main__":
    import uvicorn
    # Запускаем сервер на 0.0.0.0, чтобы он был виден снаружи контейнера
    uvicorn.run(app, host="0.0.0.0", port=8000)