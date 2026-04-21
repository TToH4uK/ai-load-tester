# Scenario Configuration Guide 📝🌐🌐

Scenarios are the heart of the **AI Load Tester**. They define the dialogue graph that both the **Bot Engine** and the **Virtual Users** follow during a test.

---

## 📄 YAML Structure

A scenario file defines a state machine. Each state (step) contains what the bot says and how it should transition to the next state based on user input.

```yaml
name: "Bank Flow Machine Pro"

steps:
  - id: "start"
    bot_say: "Hello! How can I help you today?"
    transitions:
      - to: "credit_init"
        user_say: ["I want a loan", "need money", "credit"]
        min_confidence: 0.8
      - to: "balance_check"
        user_say: ["check balance", "how much money"]
    on_fail: "rephrase_start"

  - id: "credit_init"
    bot_say: "Sure! Are you interested in a personal loan or a mortgage?"
    transitions:
      - to: "loan_info"
        user_say: ["personal", "cash"]
    on_fail: "start"
```

---

## 🛠 Anatomy of a Step

- **`id`** (string): Unique identifier for the state.
- **`bot_say`** (string): The message the bot sends when entering this state.
- **`transitions`** (list): A list of possible paths out of this state.
    - **`to`**: The ID of the target state.
    - **`user_say`** (list): Phrases that trigger this transition.
    - **`min_confidence`** (float, optional): The similarity threshold (0.0-1.0). Default is 0.7.
- **`on_fail`** (string, optional): The state to move to if no transition matches.
- **`is_final`** (boolean, optional): If true, the session resets to `start` after this message.

---

## 🧠 Shared Logic: Bot vs. Tester

One of the unique features of this framework is that the **same YAML file** drives both sides of the test:

1.  **Bot Engine**: Uses the YAML to know what to say and how to route users based on semantic similarity.
2.  **Virtual Users**: Use the YAML to know what phrases to send and what bot responses to expect.

This "Perfect Sync" ensures that you are testing the actual logic of the dialogue graph, not just random endpoints.

---

## 🛤 Advanced Flow Control

-   **Branching**: Create complex trees using multiple `transitions`.
-   **Fallback States**: Use `on_fail` to handle misunderstood inputs gracefully.
-   **Terminal States**: Mark a step with `is_final: true` to indicate the end of a successful conversation flow.

---

> [!IMPORTANT]
> **Performance Tip**: Both the Bot and the Workers load the scenario at startup. If you change the scenario, you must restart the entire stack for changes to take effect.
