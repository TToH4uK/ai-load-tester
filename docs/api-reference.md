# AI Bot API Reference 🤖🔌

The **AI Bank Bot** is the target application of the load tester. It provides a FastAPI-based interface for stateful, semantic conversation driven by YAML scenarios.

---

## 📡 Base URL
The default base URL in the Docker environment is:
`http://bank-bot:8000`

---

## 🛣 Endpoints

### 1. Send Message
Sends a message to the bot and retrieves a semantically matched response based on the current session state.

- **URL**: `/chat`
- **Method**: `POST`
- **Headers**:
    - `X-Session-ID` (string, optional): A unique identifier for the user session. If not provided, a new session is created.
- **Request Body**:
    ```json
    {
      "text": "I want to open a credit line"
    }
    ```
- **Success Response**:
    - **Code**: `200 OK`
    - **Content**:
      ```json
      {
        "text": "Certainly! We offer several types of loans. Which one are you interested in?",
        "current_step": "credit_init",
        "confidence": 0.92
      }
      ```
- **Error Responses**:
    - **Code**: `500 Internal Server Error` (embedding or engine issues)

### 2. API Documentation (Swagger)
Interactive API documentation provided by FastAPI.

- **URL**: `/docs`
- **Method**: `GET`

---

## 🛠 Internal Logic

1.  **Session Tracking**: The engine uses the `X-Session-ID` to track the user's current step in the dialogue graph.
2.  **Embedding**: The incoming `text` is converted into a vector using the `BAAI/bge-small-en-v1.5` model via `FastEmbed`.
3.  **Matrix Search**: The engine performs a dot-product similarity search against all possible transitions from the current state using `NumPy`.
4.  **State Transition**: If a match exceeds the `min_confidence` threshold, the user is moved to the new state, and the corresponding `bot_say` text is returned.

---

> [!NOTE]
> The bot automatically loads the dialogue graph from `scenarios/example.yaml` on startup. To change the bot's behavior, modify the YAML file and restart the bot container.
