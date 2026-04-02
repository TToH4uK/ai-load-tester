import time
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Bank Credit Bot Simulator")

class MessageRequest(BaseModel):
    text: str

# База знаний нашего "глупого" бота
RESPONSES = {
    "greeting": [
        "Здравствуйте! Я ваш цифровой помощник. Какой кредит вас интересует?",
        "Добрый день! Готов помочь с расчетом кредита. Какую сумму рассматриваете?",
        "Приветствую! В нашем банке лучшие ставки. Хотите узнать подробнее?"
    ],
    "rates": [
        "На текущий момент ставка по потребительскому кредиту составляет от 12.5% годовых.",
        "У нас действует акция: при страховании ставка снижается до 10.9%.",
        "Процентная ставка зависит от вашего кредитного рейтинга, в среднем это 14%."
    ],
    "calculation": [
        "При сумме 500 000 на 3 года ежемесячный платеж составит примерно 16 800 рублей.",
        "Ваша заявка предварительно одобрена. Срок кредитования до 60 месяцев.",
        "Для точного расчета мне нужно подтверждение вашего дохода через Госуслуги."
    ],
    "fallback": [
        "Извините, я не совсем понял ваш запрос. Повторите, пожалуйста.",
        "К сожалению, сейчас я не могу обработать эту операцию.",
        "Вы сказали: '{text}'. Могу я помочь чем-то другим?"
    ]
}

@app.post("/chat")
async def chat_endpoint(request: MessageRequest):
    start_time = time.time()
    user_text = request.text.lower()
    
    # Имитируем реальную задержку обработки сервером (0.1 - 0.4 сек)
    time.sleep(random.uniform(0.1, 0.4))
    
    # Логика выбора ответа
    if any(word in user_text for word in ["привет", "здравствуйте", "хочу", "взять"]):
        response_text = random.choice(RESPONSES["greeting"])
    elif any(word in user_text for word in ["ставка", "процент", "%"]):
        response_text = random.choice(RESPONSES["rates"])
    elif any(word in user_text for word in ["500", "рублей", "сумма", "год"]):
        response_text = random.choice(RESPONSES["calculation"])
    else:
        response_text = random.choice(RESPONSES["fallback"]).format(text=request.text)

    # Имитация редких ошибок сервера (5% случаев) для проверки устойчивости тестера
    # if random.random() < 0.05:
    #     raise HTTPException(status_code=500, detail="Internal Banking API Error")

    latency = time.time() - start_time
    
    return {
        "text": response_text,
        "latency": latency,
        "status": "success"
    }

if __name__ == "__main__":
    # Важно: host 0.0.0.0 чтобы Docker видел сервис
    uvicorn.run(app, host="0.0.0.0", port=8000)