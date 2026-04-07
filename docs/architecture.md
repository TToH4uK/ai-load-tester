# Architecture Overview 🏗🏢🌐

The **AI Load Tester** is a modular, distributed system designed to stress-test AI conversational agents using realistic user behavior simulations and semantic accuracy validation.

---

## 🗄️ Database Layer (`db_manager/`)

The system relies on a persistent **PostgreSQL (v15)** database enhanced with the `pgvector` extension for efficient similarity searches.

- **`pgvector` Integration**: Enables store and query of high-dimensional vectors directly in SQL.
- **SQLAlchemy ORM**: Provides a clean Pythonic interface for database operations.
- **Automated Initialization**: On startup, the bot checks for database health and populates a sample Knowledge Base (FAQ) if empty.
- **Vector Search Logic**:
  ```sql
  SELECT * FROM faq ORDER BY question_vector <=> :query_vector LIMIT 1;
  ```

---

## 🧠 Semantic Validation (`brain/`)

The validation engine ensures that the AI Bot isn't just responding, but responding *correctly* by comparing its output against expected intents.

- **Model**: Uses `all-MiniLM-L6-v2` via `sentence-transformers` for a balanced mix of speed and accuracy.
- **Caching Strategy**: Embeddings for "expected intents" defined in YAML scenarios are cached to minimize redundant CPU usage during high-load tests.
- **Scoring**: Computes cosine similarity between the bot's response and the target intent. A configurable `min_similarity` threshold determines success.

---

## 👤 Virtual User & Personas (`core/`)

Each simulated user is an independent state-machine that follows a defined YAML scenario.

- **Personas**: To simulate real-world variability, users are assigned one of three personas:
    -   **Standard**: Normal typing speed and delays.
    -   **Hurried**: 0.5x delay multiplier (fast interaction).
    -   **Detailed**: 2.0x delay multiplier (slow, deliberate interaction).
- **State Machine**: Users track their `current_step_id` and transition based on `on_success` or `on_fail` hooks.

---

## 🚀 Distributed Orchestration (Locust)

For massive scale, the tester uses a distributed **Master-Worker** architecture.

### Locust Master
- **Coordination**: Synchronizes workers and aggregates statistics.
- **Web Dashboard**: Real-time viewing of RPS, failure rates, and response time distributions.
- **No Load Generation**: The master does not generate traffic, preserving its resources for management.

### Locust Workers
- **Workload Generators**: Each worker runs multiple `VirtualUser` instances.
- **Horizontal Scaling**: Simply add more worker containers to increase the load.
- **Scenario loading**: Workers load scenarios from the `SCENARIO_PATH` independently.

---

## ⚙️ Service Orchestration (Docker)

The stack is orchestrated via `docker-compose.yml`, ensuring that all dependencies (DB, Bot, Master, Workers) are network-linked and healthy before the test begins.

---
> [!TIP]
> When scaling to extreme loads (10,000+ users), ensure your host machine has sufficient CPU for the `sentence-transformers` computations on the worker nodes.
