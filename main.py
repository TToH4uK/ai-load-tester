import sys
import os
import time
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastembed import TextEmbedding

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_manager.session import SessionLocal, init_db
from db_manager.models import FAQ

VALIDATOR_MODEL = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

app = FastAPI(title="Bank AI Bot Universal")

class ChatRequest(BaseModel):
    text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    print("🗄️ Инициализация БД...")
    for i in range(10):
        try:
            init_db()
            print("✅ База готова.")
            break
        except Exception as e:
            print(f"🔄 Ожидание БД... ({e})")
            time.sleep(3)

# --- ВАРИАНТ 1: Для нового Locust (POST /chat) ---
@app.post("/chat")
async def chat_post(request: ChatRequest, db: Session = Depends(get_db)):
    return await process_search(request.text, db)

# --- ВАРИАНТ 2: Для старого теста (GET /ask) ---
@app.get("/ask")
async def chat_get(q: str = Query(...), db: Session = Depends(get_db)):
    return await process_search(q, db)

# Общая логика поиска
async def process_search(query_text: str, db: Session):
    try:
        query_vector = list(VALIDATOR_MODEL.embed([query_text]))[0].tolist()
        best_match = db.query(FAQ).order_by(
            FAQ.question_vector.cosine_distance(query_vector)
        ).first()

        answer = best_match.answer if best_match else "Извините, ответ не найден."
        # Возвращаем и 'text' (для Locust) и 'answer' (для старых скриптов)
        return {
            "text": answer,
            "answer": answer,
            "status": "success"
        }
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))