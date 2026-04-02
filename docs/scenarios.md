# Scenario Configuration Guide 📝🌐

Scenarios are the core of **AI Load Tester**. They define the conversation flow and specify how to validate bot responses. Scenarios use a state-machine architecture where each step defines expected user input and logic for the next step.

## YAML Structure

A scenario file contains three main sections:
1. `name`: Descriptive name of the test.
2. `config`: Global settings like `base_url`, `timeout`, and `typing_delay`.
3. `steps`: An array of conversation steps.

### Example Configuration

```yaml
name: "Complex Bank Assistant Test"
config:
  base_url: "http://localhost:8000/chat"
  timeout: 5.0
  typing_delay: [1, 3] # [min, max] delay in seconds
```

## Anatomy of a Step

Each step in the `steps` array has the following properties:

- **`id`**: (Required) A unique identifier for the step.
- **`user_say`**: (Required) The text the virtual user will send to the bot. Can be a single string or a list of strings (one will be chosen randomly).
- **`validation`**: (Optional) Rules for evaluating the bot's response.
- **`on_success`**: (Required) ID of the next step if validation passes. Use `"end"` to terminate the session.
- **`on_fail`**: (Required) ID of the next step if validation fails.

### Validation Rules

The `validation` object supports several types of checks:

- **`intent`**: A string representing the expected intent or a canonical response.
- **`min_similarity`**: (Default: 0.7) The minimum cosine similarity score required for success (using `sentence-transformers`).
- **`contains`**: A list of strings. If any string in the list is present in the bot's response (case-insensitive), it overrides `intent` validation and marks the step as successful.

```yaml
validation:
  intent: "Tell me more about loans."
  min_similarity: 0.85
  contains: ["credit", "finance", "%"]
```

## Flow Control

The `on_success` and `on_fail` properties allow for complex branching:

- **Simple Linear Flow**: Each step points to the next step.
- **Retry Logic**: If a step fails, it can point back to itself or to a "rephrase" step.
- **Error Handling**: Failed steps can lead to a specific "termination" step that logs the error properly.

### Special Step IDs
- `end`: Immediately stops the virtual user session with a success status.

---

> [!TIP]
> Use a list for `user_say` to make the load test more realistic. AI models may behave differently depending on the phrasing of the user's input.
