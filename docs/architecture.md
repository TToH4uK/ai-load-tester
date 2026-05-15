# Architecture Overview 🏗🏢🌐

The **AI Load Tester** is a modular, distributed system designed to stress-test AI conversational agents using realistic user behavior simulations and semantic accuracy validation.

---

## 🤖 Bot Engine Layer (`main.py`)

The system uses a stateful, YAML-driven bot engine designed for high-performance dialogue management.

- **In-Memory Semantic Indexing**: On startup, the engine parses YAML scenarios and generates embeddings for all possible user phrases using `FastEmbed`.
- **NumPy Matrix Matching**: Instead of querying an external database, user input is converted to a vector and compared against the current state's transitions using optimized NumPy dot-product operations.
- **Session Management**: Tracks user progress through the dialogue graph using a session-based state store, enabling multi-turn conversation testing.
- **Zero-Latency Retrieval**: By keeping the knowledge base (dialogue graph) in memory, the bot can handle thousands of requests per second with sub-millisecond processing time.

---

## 🧠 Semantic Validation (`brain/`)

The validation logic ensures that the dialogue transitions are accurate by comparing user input against expected "intents" defined in the YAML.

- **Model**: Uses `BAAI/bge-small-en-v1.5` (via `FastEmbed`) for state-of-the-art semantic representation.
- **Threshold-Based Transitions**: Each transition in the dialogue graph can have a custom `min_confidence` score, ensuring the bot only advances when it is certain of the user's intent.
- **Fallback Logic**: If no transition matches the required threshold, the engine automatically triggers an `on_fail` transition to a rephrase or help state.

---

## 👤 Virtual User & Personas (`core/`)

Each simulated user in the Load Generation Layer is an independent state-machine that follows a defined YAML scenario.

- **Personas**: To simulate real-world variability, users are assigned one of three personas:
    -   **Standard**: Normal typing speed and delays.
    -   **Hurried**: 0.5x delay multiplier (fast interaction).
    -   **Detailed**: 2.0x delay multiplier (slow, deliberate interaction).
- **State Machine**: Users track their `current_step_id` and transition based on the bot's response and state indicators.

---

## 🚀 Distributed Orchestration (Locust)

For massive scale, the tester uses a distributed **Master-Worker** architecture.

### Locust Master
- **Coordination**: Synchronizes workers and aggregates statistics.
- **Web Dashboard**: Real-time viewing of RPS, failure rates, and response time distributions.

### Locust Workers
- **Workload Generators**: Each worker runs multiple `VirtualUser` instances.
- **Horizontal Scaling**: Simply add more worker containers to increase the load.

---

## 📈 Monitoring & Observability

The AI Load Tester includes a comprehensive observability stack.

- **Prometheus**: Scrapes load metrics and bot engine performance data directly from the system.
- **Grafana**: Provides rich, real-time dashboards to visualize virtual user activity, semantic matching confidence scores, latency, and success rates.

---

## ⚙️ Service Orchestration (Docker)

The stack is orchestrated via `docker-compose.yml`, ensuring that the Bot Engine and Locust nodes are network-linked and healthy before the test begins.

---
> [!TIP]
> When scaling to extreme loads (10,000+ users), ensure your host machine has sufficient CPU for the embedding computations on the bot node.
