# Distributed AI Load Tester 🧠🚀🌐

**AI Load Tester** is an advanced, distributed framework for evaluating AI-driven conversational agents. It features a modern stack with **PostgreSQL**, **FastAPI**, and **Locust**, designed to simulate thousands of users interacting with a knowledge-based AI bot.

## 🏗 System Architecture

The project now follows a distributed service-oriented architecture:

1.  **PostgreSQL DB**: Stores the AI's Knowledge Base (FAQ) for semantic retrieval.
2.  **Bank AI Bot (FastAPI)**: An AI-powered mock assistant that simulates response generation by querying the DB.
3.  **Locust Master**: Orchestrates the load test and provides a web dashboard for real-time monitoring.
4.  **Locust Workers**: Distributed nodes that generate the actual traffic, allowing for massive scale.

## ✨ Key Features

-   **Semantic Validation**: Uses `sentence-transformers` to evaluate bot responses based on intent similarity, not just string matching.
-   **Distributed Scaling**: Easily scale up testing capacity by adding more Locust worker containers.
-   **Persistent Knowledge Base**: All AI responses are managed via a PostgreSQL database with SQLAlchemy ORM.
-   **Automated Initialization**: The system automatically waits for the database to be healthy and populates it with sample data on startup.

## 🚀 Quick Start (with Docker)

The easiest way to run the entire stack is using **Docker Compose**:

```bash
# Start the full stack (DB, Bot, and Locust Master)
docker compose up -d

# Scale the number of Locust workers for a heavy test
docker compose up -d --scale locust-worker=3
```

-   **Locust Web UI**: [http://localhost:8089](http://localhost:8089)
-   **AI Bot API**: [http://localhost:8000](http://localhost:8000)
-   **PostgreSQL**: `localhost:5432`

## 🛠 Project Structure

-   `db_manager/`: PostgreSQL models and database session management.
-   `brain/`: NLP logic and semantic similarity validation.
-   `scenarios/`: YAML-based definitions of user-bot interaction flows.
-   `main.py`: The FastAPI-based AI Bot server.
-   `locustfile.py`: The load tester configuration for Locust workers.
-   `docs/`: Detailed technical documentation.

## 📝 Configuration

Key environment variables in `docker-compose.yml`:
-   `DATABASE_URL`: Connection string for PostgreSQL.
-   `TARGET_URL`: The bot's API endpoint (e.g., `http://bank-bot:8000`).
-   `SCENARIO_PATH`: Path to the YAML scenario file to be used for testing.

## 📚 Learn More

-   [Architecture Deep Dive](docs/architecture.md)
-   [Scenario Configuration Guide](docs/scenarios.md)

---
Built for high-performance AI reliability testing.
