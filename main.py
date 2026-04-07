import sys
import os
import time
import yaml
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastembed import TextEmbedding

# Add paths so Python can see your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_manager.session import SessionLocal, init_db
from db_manager.models import FAQ

VALIDATOR_MODEL = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

app = FastAPI(title="Bank AI Bot Optimized")

# Global variables

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    print("🗄️ Connecting to PostgreSQL...")
    # Wait for database accessibility
    for i in range(10):
        try:
            init_db()
            with SessionLocal() as db:
                if db.query(FAQ).count() == 0:
                    print("📝 Populating database with test data...")
                    db.add_all([
                        FAQ(question="How to open an account?", answer="In the app or branch with a passport."),
                        FAQ(question="Card limit", answer="Standard limit is 500,000 RUB per day."),
                        FAQ(question="Where is my cashback?", answer="Accrued on the 10th of every month.")
                    ])
                    db.commit()
            print("✅ Database is ready.")
            break
        except Exception as e:
            print(f"🔄 Attempt {i+1}: Database not reachable yet... ({e})")
            time.sleep(3)

    print("🚀 Loading FastEmbed (ONNX Runtime)...")
    # Using bge-small-en-v1.5 - it is very fast and lightweight
    print("✅ System fully ready for load testing.")

@app.get("/ask")
def ask_bot(q: str, db: Session = Depends(get_db)):
    if not q:
        raise HTTPException(status_code=400, detail="Query is empty")

    try:
        # Compute query vector
        query_vector = list(VALIDATOR_MODEL.embed([q]))[0].tolist()

        # Perform vector search
        best_match = db.query(FAQ).order_by(
            FAQ.question_vector.cosine_distance(query_vector)
        ).first()

        if best_match:
            return {
                "answer": best_match.answer,
                "matched_question": best_match.question,
                "source": "vector_search"
            }
        
        return {"answer": "Sorry, I couldn't find an answer.", "source": "fallback"}

    except Exception as e:
        print(f"❌ Processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

#if __name__ == "__main__":
#    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4)