## 🎯 Goal: Master Agentic AI & Reasoning Models

> **The 2025 Shift**: We are moving from **Chatbots** (which talk) to **Agents** (which act). The engine powering this shift is **Reasoning Models** (like DeepSeek-R1 and OpenAI o1).

Today, we cover the cutting edge of AI System Design: **Agentic Workflows** and the **Reasoning Models** that make them reliable.

---

## 📈 The Trend: Why Agentic AI?

In 2023-2024, the focus was on RAG (Retrieval-Augmented Generation) to make LLMs "know" things.
In 2025, the focus is on **Agents** to make LLMs "do" things.

### Chatbot vs. Agent
| Feature | Chatbot (e.g., ChatGPT 3.5) | Agent (e.g., Devin, Operator) |
| :--- | :--- | :--- |
| **Role** | Passive Informant | Active Worker |
| **Output** | Text | Actions (API calls, SQL queries) |
| **Loop** | User $\to$ Bot $\to$ User | User $\to$ Agent $\to$ **Tool** $\to$ Agent $\to$ User |
| **Failure Mode** | Hallucination | Infinite Loops / Bad Tool Use |

---

## 🧩 Core Concept: The ReAct Pattern

The **ReAct** (Reasoning + Acting) pattern is the foundation of modern agents. Instead of asking the LLM to solve a problem in one go, we force it to:
1.  **Reason**: "Thought: I need to check the weather."
2.  **Act**: "Action: `get_weather(NYC)`"
3.  **Observe**: "Observation: Sunny, 25C"
4.  **Reason**: "Thought: It's sunny, I can answer."
5.  **Answer**: "Final Answer: It is sunny."

### 💻 Code Example: Simple ReAct Loop
This is how frameworks like LangChain work under the hood.

```python
import re

class MockLLM:
    """Simulates an LLM trained for ReAct"""
    def generate(self, prompt):
        # In reality, this calls an API (GPT-4 / DeepSeek-V3)
        if "weather" in prompt and "Observation" not in prompt:
            return "Thought: I need to check the weather.\nAction: getWeather(New York)"
        if "Observation: Sunny" in prompt:
            return "Thought: I have the data.\nFinal Answer: It is sunny in New York."
        return "Final Answer: I don't know."

def react_loop(query):
    llm = MockLLM()
    history = f"Question: {query}\n"

    # Safety Limit: Prevent infinite loops
    for i in range(5):
        response = llm.generate(history)
        history += response + "\n"

        if "Final Answer:" in response:
            return response.split("Final Answer:")[1].strip()

        if "Action:" in response:
            # 1. Parse Tool
            action = response.split("Action:")[1].strip()
            # 2. Execute Tool (Mocked here)
            if "getWeather" in action:
                obs = "Sunny, 25C"
                # 3. Feed Observation back
                history += f"Observation: {obs}\n"

    return "Timeout"
```

---

## 🔬 Deep Dive: DeepSeek-R1 (The Reasoning Engine)

Reliable Agents need **Reasoning Models**. If an agent can't "think" before it acts, it will call the wrong APIs (e.g., deleting a database instead of reading it).

**Paper**: *"DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"*

### 1. The Trap: Why standard LLMs fail at Agents
Standard LLMs (like Llama 3 or GPT-4o-mini) are trained on **Next Token Prediction**. They try to guess the answer immediately.
*   *User*: "Plan a trip to Tokyo."
*   *Standard LLM*: *Immediately starts listing hotels (hallucinating availability).*
*   *Agent Needs*: "Wait, I need to check flight APIs first, then hotel APIs."

### 2. The Fix: Chain of Thought (CoT) via RL
DeepSeek-R1 (and OpenAI o1) introduces a **thinking phase**. The model is trained to output a long `<think>` block before the final answer.

**Key Innovation: GRPO (Group Relative Policy Optimization)**
Instead of needing a separate "Critic" model (which is expensive and slow) like in PPO (Proximal Policy Optimization), DeepSeek-R1 uses **GRPO**.

*   **Logic**: Generate a *group* of outputs for the same prompt.
*   **Reward**: Calculate the average reward of the group.
*   **Update**: Boost the outputs that did better than the group average.

$$ Advantage_i = \frac{Reward_i - Average(Group Rewards)}{StandardDeviation(Group Rewards)} $$

### 💻 Code Simulation: GRPO Advantage
This shows how the model learns which "thought process" was better without a critic.

```python
import numpy as np

def calculate_grpo_advantage(rewards):
    """
    If Model generates 4 solutions with rewards [0.1, 0.9, 0.2, 0.8]:
    - The 0.9 solution gets a huge positive boost (doing better than peers).
    - The 0.1 solution gets a negative penalty.
    """
    rewards = np.array(rewards)
    mean = np.mean(rewards)
    std = np.std(rewards)
    # Normalize: How good is this specific answer compared to the others?
    return (rewards - mean) / (std + 1e-8)

rewards = [0.2, 0.9, 0.1, 0.85]
# Result: [-0.85, 1.06, -1.13, 0.92] -> The model learns to favor behaviors 2 and 4.
```

### 3. Production Realities
*   **Cold Start**: RL is unstable. DeepSeek used a small "Cold Start" dataset of high-quality CoT examples to prime the model before RL.
*   **Distillation**: DeepSeek-R1-Zero (pure RL) was smart but spoke poorly. They "distilled" its reasoning patterns into smaller, cleaner models for production.

---

## ⚔️ Interview Post-Mortem: Design an AI Travel Agent

**The Question**: "Design an AI system that books flights for users."

### ❌ The Trap (Junior Engineer)
*   "I'll just prompt GPT-4 to 'Book a flight from NYC to LA'."
*   **Why it fails**: LLMs cannot access private tools. They will hallucinate "Flight AA123 confirmed".

### 🔫 The Kill Shot (Senior Engineer)
*   "We need an **Agentic Workflow** with **Tool Definitions**."
*   "The System has 3 layers:
    1.  **Planner (Reasoning Model)**: Decomposes 'Book flight' into `[Search, Select, Book]`.
    2.  **Tool Executor**: A secure sandbox that calls the `Amadeus` or `Sabre` API.
    3.  **Memory**: Stores the user's passport details (Vector DB) and current session state (Redis)."

### 🛠 The Fix (Architecture)
1.  **User Request**: "Book a flight..."
2.  **Router**: Sends to **DeepSeek-R1** (or similar) to generate a Plan.
3.  **Loop**:
    *   *Step 1*: Agent calls `search_flights(source, dest)`.
    *   *Step 2*: App executes API. Returns JSON.
    *   *Step 3*: Agent analyzes JSON. Calls `book_flight(id)`.
4.  **Human-in-the-loop**: For the final `book` action, require user confirmation (Crucial for safety).

---

## ⚡ Flashcards

1.  **What is the core difference between a Chatbot and an Agent?**
    *   Chatbots output text; Agents output *actions* (tool calls) to perform tasks.

2.  **What is the ReAct pattern?**
    *   Reason + Act. A loop where the model thinks, acts (calls tool), observes the result, and repeats.

3.  **What is GRPO in DeepSeek-R1?**
    *   Group Relative Policy Optimization. A Reinforcement Learning method that normalizes rewards within a group of outputs for the same prompt, removing the need for a Critic model.

4.  **Why do Agents need "Reasoning Models" (like o1/R1)?**
    *   Agents must plan multi-step workflows without hallucinating. Standard models often skip steps or fail to recover from tool errors.

5.  **What is "Cold Start" in RL training?**
    *   Priming the model with a small set of high-quality examples (Supervised Fine-Tuning) before starting Reinforcement Learning, to prevent the model from collapsing into nonsense.
