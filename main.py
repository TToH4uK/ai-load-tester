import os
import yaml
import uuid
import logging
import numpy as np
import sys
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastembed import TextEmbedding
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram, Counter, Gauge

# Настройка логирования — выводим всё сразу в stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML-Powered Bot Engine")
instrumentator = Instrumentator().instrument(app)

# Метрики
SEARCH_LATENCY = Histogram("bot_vector_search_duration_seconds", "Latency", buckets=(.001, .01, .1, .5, 1.0))
CONFIDENCE_VALUE = Gauge("bot_last_confidence_score", "Confidence")
MATCH_COUNT = Counter("bot_matches_total", "Matches")
FALLBACK_COUNT = Counter("bot_fallbacks_total", "Fallbacks")
INTENT_USAGE = Counter("bot_intent_usage_total", "Intents", ["from_step", "to_step"])
TRUE_POSITIVES = Counter("bot_tp_total", "TP")
FALSE_POSITIVES = Counter("bot_fp_total", "FP")
FALSE_NEGATIVES = Counter("bot_fn_total", "FN")

# --- Новые метрики для расчета Hit Ratio ---
CACHE_HITS = Counter("bot_cache_hits_total", "Total number of embedding cache hits")
CACHE_MISSES = Counter("bot_cache_misses_total", "Total number of embedding cache misses")

MODEL = None
SCENARIO = {}
VECTOR_CACHE = {}
USER_SESSIONS = {}

# --- Кэш для эмбеддингов входящих запросов ---
# Хранит структуру вида: {"очищенный текст": numpy_array_вектор}
EMBEDDING_CACHE = {}
MAX_CACHE_SIZE = 10000

class ChatRequest(BaseModel):
    text: str

@app.on_event("startup")
async def startup():
    global SCENARIO, VECTOR_CACHE, MODEL
    instrumentator.expose(app)
    logger.info("🚀 Сервер запущен. Ожидание загрузки модели...")

    try:
        logger.info("⏳ Скачивание модели BAAI/bge-small-en-v1.5 из Hugging Face...")
        MODEL = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        logger.info("✅ Модель загружена успешно.")

        with open("scenarios/example.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            SCENARIO = {step["id"]: step for step in data["steps"]}
        
        logger.info("⏳ Индексация векторов...")
        for step_id, step in SCENARIO.items():
            VECTOR_CACHE[step_id] = []
            for trans in step.get("transitions", []):
                phrases = trans.get("user_say", [])
                if isinstance(phrases, str): phrases = [phrases]
                
                phrase_vectors = np.array(list(MODEL.embed(phrases)))
                VECTOR_CACHE[step_id].append({
                    "to": trans["to"],
                    "matrix": phrase_vectors,
                    "min_conf": trans.get("min_confidence", 0.7)
                })
        logger.info("✅ Бот полностью готов.")
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА СТАРТА: {e}")
        sys.exit(1)

@app.post("/chat")
async def chat(request: ChatRequest, x_session_id: str = Header(None), x_expected_intent: str = Header(None)):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model initializing...")
    
    session_id = x_session_id or str(uuid.uuid4())
    current_step_id = USER_SESSIONS.get(session_id, "start")
    step_data = SCENARIO.get(current_step_id, SCENARIO.get("start"))
    
    # Нормализуем текст для кэш-ключей (убираем лишние пробелы, приводим к нижнему регистру)
    clean_text = request.text.strip().lower()
    
    best_target, max_score, final_threshold = None, 0.0, 0.7

    # Запускаем таймер на весь процесс поиска (включая векторизацию, если она будет)
    with SEARCH_LATENCY.time():
        # 1. Проверяем кэш эмбеддингов
        if clean_text in EMBEDDING_CACHE:
            CACHE_HITS.inc()
            query_vec = EMBEDDING_CACHE[clean_text]
        else:
            CACHE_MISSES.inc()
            # Генерируем новый вектор через нейросеть
            query_vec = list(MODEL.embed([request.text]))[0]
            
            # Сохраняем вектор в кэш, если лимит не превышен
            if len(EMBEDDING_CACHE) < MAX_CACHE_SIZE:
                EMBEDDING_CACHE[clean_text] = query_vec

        # 2. Матричное вычисление косинусного сходства
        for trans in VECTOR_CACHE.get(current_step_id, []):
            scores = np.dot(trans["matrix"], query_vec)
            top_score = np.max(scores)
            if top_score > max_score:
                max_score, best_target, final_threshold = top_score, trans["to"], trans["min_conf"]

    CONFIDENCE_VALUE.set(max_score)
    is_match = bool(best_target and max_score >= final_threshold)
    new_step_id = best_target if is_match else step_data.get("on_fail", current_step_id)

    if is_match:
        MATCH_COUNT.inc()
        INTENT_USAGE.labels(from_step=current_step_id, to_step=new_step_id).inc()
    else:
        FALLBACK_COUNT.inc()

    if x_expected_intent:
        if is_match and best_target == x_expected_intent:
            TRUE_POSITIVES.inc()
        elif is_match and best_target != x_expected_intent:
            FALSE_POSITIVES.inc()
        elif not is_match and any(t['to'] == x_expected_intent for t in step_data.get("transitions", [])):
            FALSE_NEGATIVES.inc()

    USER_SESSIONS[session_id] = "start" if SCENARIO.get(new_step_id, {}).get("is_final") else new_step_id
    return {
        "text": SCENARIO.get(new_step_id, {}).get("bot_say", "Error"),
        "confidence": round(float(max_score), 2),
        "step": new_step_id
    }