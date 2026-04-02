from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import random
import asyncio

# Наши импорты из папки db_manager
from db_manager.session import SessionLocal, init_db
from db_manager.models import FAQ

app = FastAPI(title="Smart Bank Mock")

# Зависимость для БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/ask")
async def ask_endpoint(q: str, db: Session = Depends(get_db)):
    # Имитируем сетевую задержку (как в твоем старом коде)
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    # 1. Пробуем найти ответ по ключевому слову в БД
    # SQL: SELECT * FROM faq WHERE question ILIKE '%слово%'
    result = db.query(FAQ).filter(FAQ.question.ilike(f"%{q}%")).first()
    
    if result:
        return {
            "answer": result.answer,
            "source": "postgres_mock",
            "status": "success"
        }

    # 2. Если ничего не нашли — берем fallback из базы (или дефолт)
    return {
        "answer": f"Я получил ваш запрос: '{q}', но в моей базе знаний нет подходящего ответа.",
        "source": "fallback",
        "status": "not_found"
    }