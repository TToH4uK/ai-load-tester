# Architecture Overview 🏗🏢

The **AI Load Tester** is an event-driven system built with Python's `asyncio` for maximum performance and concurrency. It consists of multiple modules, each handling a specific part of the load testing process.

## 🧠 Brain (`brain/`)

The **Brain** module is the NLP engine of the project. It uses the `sentence-transformers` library to compute semantic similarities between bot responses and expected outcomes.

### `SemanticValidator`
- **Model**: `all-MiniLM-L6-v2` (Lightweight and fast).
- **Caching**: Results of computing embeddings for repetitive parts (like the expected intent from YAML) are cached to reduce CPU usage.
- **Cosine Similarity**: Comparing two vectors representing text allows for more precise evaluation than simple regex or keyword matching.

## 👤 Core (`core/`)

The **Core** module manages the simulation of users.

### `VirtualUser`
- Each virtual user is an asynchronous task.
- **Protocol Agnostic**: The `VirtualUser` communicates with the bot via a configurable protocol (HTTPS by default).
- **Typing Simulation**: Emulates human typing delays based on the `typing_delay` setting in the scenario.
- **Persona System**: Assigns each user a "persona" (hurried, detailed, standard) that further adjusts typing speeds and potentially their phrasing.

## 📊 Monitoring (`monitoring/`)

The **Monitoring** module captures real-time data from every virtual user's interaction.

### `StatsCollector`
- Aggregates latency, success/failure counts, and semantic similarity scores.
- Provides reports in CSV format (`final_report.csv`) for post-test analysis.
- Detailed logs for each user session are stored in the `reports/` directory.

## 🚀 Scaling with Locust

For high-scale testing, the **AI Load Tester** integrates with [Locust.io](https://locust.io/).

- **`locustfile.py`**: A custom implementation that wraps the `VirtualUser` logic into Locust's `HttpUser`.
- **Parallel Computing**: Vector computations (which can be CPU-intensive) are offloaded to a `ThreadPoolExecutor` to prevent blocking the main Locust event loop.

---

> [!NOTE]
> The default configuration uses the CPU for vector computations. For extremely large tests, using a CUDA-compatible GPU is recommended.
