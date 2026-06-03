from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import random
import asyncio

# Наши импорты из папки db_manager
from db_manager.session import SessionLocal, init_db
from db_manager.models import FAQ

app = FastAPI(title="Smart Bank Mock")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/ask")
async def ask_endpoint(q: str, db: Session = Depends(get_db)):
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    result = db.query(FAQ).filter(FAQ.question.ilike(f"%{q}%")).first()
    
    if result:
        return {
            "answer": result.answer,
            "source": "postgres_mock",
            "status": "success"
        }
    
    return {
        "answer": f"Я получил ваш запрос: '{q}', но в моей базе знаний нет подходящего ответа.",
        "source": "fallback",
        "status": "not_found"
    }