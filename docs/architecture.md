# Architecture Overview 🏗🏢🌐

The **AI Load Tester** is now a full-stack, distributed system featuring a persistent knowledge base and a scalable load testing infrastructure. The system is designed to handle thousands of concurrent AI-user interactions.

## 🗄️ Database Layer (`db_manager/`)

The system now integrates a persistent **PostgreSQL (v15)** database to manage the bot's Knowledge Base.

- **SQLAlchemy ORM**: Used for database interactions, with models defined in `models.py`.
- **Knowledge Base (FAQ)**: Stores canonical pairs of questions and answers.
- **Initialization**: The bot automatically checks for database health and populates it with a sample FAQ if empty on startup.

## 🧠 Brain (`brain/`)

The **Brain** module remains the AI engine of the project, compute semantic similarities between bot responses and expected outcomes.

- **Sentence Embeddings**: Each bot response is compared against the "expected intent" using the lightweight `all-MiniLM-L6-v2` model.
- **Performance**: In distributed mode, vector computations are performed on the worker nodes, distributing the CPU load and preventing the Locust Master from becoming a bottleneck.

## 🚀 Distributed Scaling (Locust)

For massive scale, the tester uses a **Master-Worker** architecture.

### Locust Master
- Orchestrates the test, synchronizes workers, and collects aggregate statistics.
- Provides a real-time web dashboard (Port 8089) for monitoring latency, success rates, and semantic score distributions.

### Locust Workers
- The actual load generators.
- Each worker executes the code defined in `locustfile.py`.
- **Horizontal Scaling**: You can scale out the test by adding more worker containers (`docker compose up --scale locust-worker=N`).

## ⚙️ Service Orchestration (Docker Compose)

The entire stack is managed via a single `docker-compose.yml` file, which includes:

1.  **`db`**: PostgreSQL 15 with healthchecks to ensure service readiness.
2.  **`bank-bot`**: The FastAPI-based AI server.
3.  **`locust-master`**: The central coordination hub for the load test.
4.  **`locust-worker`**: Distributed workload generators.

---

> [!NOTE]
> The AI Bot and the Load Tester are separate services. The Bot acts as the **Target App**, while the Locust nodes act as the **Tester**.
