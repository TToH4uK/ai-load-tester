# AI Bot API Reference 🤖🔌

The **AI Bank Bot** is the target application of the load tester. It provides a FastAPI-based interface for semantic question answering from a persistent knowledge base.

---

## 📡 Base URL
The default base URL in the Docker environment is:
`http://bank-bot:8000`

---

## 🛣 Endpoints

### 1. Ask a Question
Retrieves the most semantically relevant answer from the Knowledge Base.

- **URL**: `/ask`
- **Method**: `GET`
- **Parameters**:
    - `q` (string, required): The user's question or query.
- **Success Response**:
    - **Code**: `200 OK`
    - **Content**:
      ```json
      {
        "answer": "Standard limit is 500,000 RUB per day.",
        "matched_question": "What is my card limit?",
        "source": "vector_search"
      }
      ```
- **Error Responses**:
    - **Code**: `400 Bad Request` (if `q` is empty)
    - **Code**: `500 Internal Server Error` (database or embedding issues)

### 2. API Documentation (Swagger)
Interactive API documentation provided by FastAPI.

- **URL**: `/docs`
- **Method**: `GET`

---

## 🛠 Internal Logic

1.  **Embedding**: The query string `q` is converted into a 384-dimensional vector using the `BAAI/bge-small-en-v1.5` model via `FastEmbed`.
2.  **Vector Search**: The system performs a cosine distance search in the PostgreSQL `faq` table using `pgvector`.
3.  **Result Retrieval**: The entry with the smallest cosine distance (highest similarity) is returned. If no close match is found, a fallback response is provided.

---

> [!NOTE]
> The bot automatically initializes its database on the first run with several sample banking questions. You can modify these in `main.py`.
