# Scenario Configuration Guide 📝🌐🌐

Scenarios define the user-AI interaction flow for **AI Load Tester**. They represent a state-machine that guides the virtual users through potential conversation paths.

---

## 📄 YAML Structure

A scenario file is composed of three main sections: `name`, `config`, and `steps`.

```yaml
name: "Complex Bank Assistant Test"

config:
  base_url: "http://bank-bot:8000"
  timeout: 5.0
  typing_delay: [2, 4] # Min and Max delay in seconds between messages

steps:
  - id: "start"
    user_say: ["Hello", "Hi there"]
    validation:
      intent: "greeting"
      min_similarity: 0.8
    on_success: "check_balance"
    on_fail: "rephrase_start"
```

---

## 🛠 Anatomy of a Step

Each step instructs the `VirtualUser` on what to say and how to evaluate the AI's response.

- **`id`** (string): Unique identifier for the step.
- **`user_say`** (string | list): The message(s) the user will send. If a list is provided, one is chosen at random.
- **`validation`** (object): Rules for scoring the bot's response.
- **`on_success`** (string): The ID of the next step if validation passes.
- **`on_fail`** (string): The ID of the next step if validation fails.

---

## ✅ Validation Rules

The system supports two primary types of validation:

### 1. Semantic Validation (`intent`)
Uses vector embeddings to compare the bot's response against a target "intent" string.
-   **`intent`**: The semantic target.
-   **`min_similarity`**: (Default: 0.7) The cosine similarity threshold (0.0 to 1.0).

### 2. Keyword Validation (`contains`)
Checks if the bot's response contains specific substrings.
-   **`contains`**: A list of strings. If any string is found (case-insensitive), validation passes.

---

## 🛤 Advanced Flow Control

-   **Branching**: Use `on_success` and `on_fail` to create complex conversation trees.
-   **Retries**: Point `on_fail` back to a "rephrase" step or the same step to simulate user persistence.
-   **Termination**: Use the special ID `"end"` to successfully complete a session. Any ID not found in the `steps` list will also terminate the user.

---

> [!IMPORTANT]
> **Performance Tip**: Workers load the scenario file once at startup. If you modify the scenario, you must restart the Locust workers for changes to take effect.
