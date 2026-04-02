# AI Load Tester 🧠🚀

**AI Load Tester** is a specialized framework designed to evaluate the performance and reliability of AI-driven conversational agents (LLM bots, customer service assistants, etc.). Unlike traditional load testers that focus on simple HTTP status codes, this tool uses **semantic validation** to ensure the AI's responses are contextually relevant even under heavy load.

## ✨ Key Features

- **Semantic Validation**: Uses `sentence-transformers` to compare bot responses with expected intents or user goals using cosine similarity.
- **Dynamic Scenarios**: Define complex conversation flows as state machines in YAML.
- **Locust Integration**: Scales from single-user tests to thousands of concurrent users using the Locust framework.
- **Persona Emulation**: Simulates different user behaviors (hurried, detailed, standard) with variable typing speeds.
- **Docker Ready**: Fully containerized environment for both the tester and a sample mock bot.

## 🏗 Project Structure

- `core/`: The heart of the tester, containing the asynchronous `VirtualUser`.
- `brain/`: Intelligence layer featuring the `SemanticValidator` for NLP-based checks.
- `scenarios/`: YAML-based test scenario definitions.
- `monitoring/`: Real-time statistics collection and reporting.
- `target_apps/`: Contains a `mock_bot.py` for testing and demonstration.
- `locustfile.py`: Bridge for high-scale testing with Locust.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- Docker & Docker Compose (optional, for containerized run)

### 2. Local Setup
```bash
# Clone the repository
git clone <repo-url>
cd ai-load-tester

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-locust.txt
```

### 3. Run a Quick Test
Start the mock bot in one terminal:
```bash
python target_apps/mock_bot.py
```
Run the load tester in another:
```bash
python main.py
```

### 4. High-Scale Testing with Locust
```bash
locust -f locustfile.py --host http://localhost:8000
```
Then open [http://localhost:8089](http://localhost:8089) in your browser.

### 5. Running with Docker
```bash
docker-compose up --build
```
This will start both the mock bot and Locust. Access the Locust UI at port 8089.

## 📝 Scenario Configuration
Scenarios are defined in `scenarios/example.yaml`. A step looks like this:

```yaml
- id: "check_rate"
  user_say: ["What is your interest rate?", "How much percent?"]
  validation:
    intent: "loan_interest_rate"
    min_similarity: 0.8
  on_success: "ask_amount"
  on_fail: "terminate"
```

For more details, see:
- [Scenario Guide](docs/scenarios.md)
- [Architecture Overview](docs/architecture.md)

## 📊 Reports
After execution, results are saved to `final_report.csv` and detailed logs are available in the `reports/` directory.

