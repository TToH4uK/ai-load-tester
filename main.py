import os
import yaml
import uuid
import logging
import numpy as np
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastembed import TextEmbedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pro Stateful Bot Engine")

MODEL = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

SCENARIO = {}
USER_SESSIONS = {}
VECTOR_CACHE = {} 

class ChatRequest(BaseModel):
    text: str

@app.on_event("startup")
async def startup():
    global SCENARIO, VECTOR_CACHE
    try:
        with open("scenarios/example.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            SCENARIO = {step["id"]: step for step in data["steps"]}
        
        logger.info("⏳ Индексация графа диалогов...")
        for step_id, step in SCENARIO.items():
            VECTOR_CACHE[step_id] = []
            for trans in step.get("transitions", []):
                phrases = trans.get("user_say", [])
                if isinstance(phrases, str): phrases = [phrases]
                
                # Храним векторы как матрицу NumPy для быстрых расчетов
                phrase_vectors = np.array(list(MODEL.embed(phrases)))
                
                VECTOR_CACHE[step_id].append({
                    "to": trans["to"],
                    "matrix": phrase_vectors,
                    # Порог теперь можно вешать на конкретный переход в YAML!
                    "min_conf": trans.get("min_confidence", 0.7)
                })
        logger.info("✅ Движок готов. Жду нагрузку.")
    except Exception as e:
        logger.error(f"❌ Ошибка старта: {e}")

@app.post("/chat")
async def chat(request: ChatRequest, x_session_id: str = Header(None)):
    try:
        session_id = x_session_id or str(uuid.uuid4())
        current_step_id = USER_SESSIONS.get(session_id, "start")
        
        if current_step_id not in SCENARIO:
            current_step_id = "start"
            
        step_data = SCENARIO[current_step_id]
        query_vec = list(MODEL.embed([request.text]))[0]

        best_target = None
        max_score = 0.0
        final_threshold = 0.7 # Дефолт

        # МАТРИЧНЫЙ ПОИСК (БЕЗ ЦИКЛОВ ПО ФРАЗАМ)
        step_transitions = VECTOR_CACHE.get(current_step_id, [])
        for trans in step_transitions:
            # Считаем сходство со всеми фразами перехода ОДНИМ махом
            scores = np.dot(trans["matrix"], query_vec)
            top_score = np.max(scores)
            
            if top_score > max_score:
                max_score = top_score
                best_target = trans["to"]
                final_threshold = trans["min_conf"]

        # Логика перехода
        if best_target and max_score >= final_threshold:
            new_step_id = best_target
            match_status = "✅ MATCH"
        else:
            new_step_id = step_data.get("on_fail", current_step_id)
            match_status = "❌ FALLBACK"

        response_text = SCENARIO.get(new_step_id, {}).get("bot_say", "Ошибка сценария")

        # Логируем для отладки семантики
        logger.info(f"[{session_id[:6]}] {current_step_id} -> {new_step_id} | In: '{request.text}' | Score: {max_score:.2f} {match_status}")

        # Управление состоянием
        if SCENARIO.get(new_step_id, {}).get("is_final"):
            USER_SESSIONS[session_id] = "start"
        else:
            USER_SESSIONS[session_id] = new_step_id

        return {
            "text": response_text,
            "current_step": new_step_id,
            "confidence": round(float(max_score), 2)
        }

    except Exception as e:
        logger.error(f"💥 Critical: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")