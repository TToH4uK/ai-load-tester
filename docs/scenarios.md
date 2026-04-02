# Scenario Configuration Guide 📝🌐🌐

Scenarios define the user-AI interaction flow for **AI Load Tester**. They represent a state-machine that guides the virtual users through potential conversation paths.

## YAML Structure

A scenario file contains:
1. `name`: Description of the test scenario.
2. `config`: Global settings (URL, timeout, delay).
3. `steps`: An array of conversation steps.

```yaml
name: "Complex Bank Assistant Test"
config:
  base_url: "http://bank-bot:8000"
  timeout: 5.0
  typing_delay: [2, 4]
```

## Anatomy of a Step

Each step defines what the user says and how the AI response is validated.

- **`id`**: Unique identifier for the step.
- **`user_say`**: Text or list of texts the user will send to the AI.
- **`validation`**: Rules for scoring the AI's response (see below).
- **`on_success`**: ID of the next step if validation passes.
- **`on_fail`**: ID of the next step if validation fails.

### API Endpoint Note

> [!IMPORTANT]
> The current **AI Bot** implementation primarily uses the `/ask` GET endpoint. The virtual users automatically append the `user_say` text as the `q` parameter (e.g., `/ask?q=...`).

### Validation Rules

AI responses are expected in JSON format: `{"answer": "...", "source": "..."}`.

- **`intent`**: The semantic target for similarity scoring.
- **`min_similarity`**: (Default: 0.7) The threshold for success.
- **`contains`**: List of strings for keyword-based success.

```yaml
validation:
  intent: "Our interest rates start from 12%."
  min_similarity: 0.8
```

## Advanced Flow Control

-   **Retry Logic**: Point `on_fail` to a "rephrase" step to simulate a user trying to clarify their question.
-   **Terminal States**: Use `on_success: "end"` or `on_fail: "end"` to stop the virtual session.

---

> [!TIP]
> Each Locust worker loads the scenario independently from the path defined in the `SCENARIO_PATH` environment variable. Ensure the file is accessible to all worker containers.
