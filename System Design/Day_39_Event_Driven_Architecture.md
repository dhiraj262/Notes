# Day 39: Event-Driven Architecture

## 🎯 Goal
Understand the shift from **Request-Driven** (REST/RPC) to **Event-Driven** (Pub-Sub).
**Focus**: Decoupling, Extensibility, and "Choreography".

---

## 🧩 Key Concepts

### 1. Request-Driven vs Event-Driven
*   **Request-Driven (Orchestration)**: Service A tells B to do X. Then tells C to do Y. A is the boss.
    *   *Pro*: Easy to trace logic.
    *   *Con*: Tight coupling. If C changes, A might need to change.
*   **Event-Driven (Choreography)**: Service A yells "User Signed Up!". B, C, and D hear it and decide what to do.
    *   *Pro*: Loose coupling. You can add Service E without touching A.
    *   *Con*: "Event Hell". Hard to see the big picture flow.

### 2. Pub-Sub Pattern (Publish-Subscribe)
*   **Publisher**: Emits events without knowing who is listening.
*   **Subscriber**: Listens for specific topics.
*   **Broker**: The middleman (Kafka, SNS, RabbitMQ).

### 3. Event Sourcing (Brief)
*   Instead of storing just the *current state* (Balance: $100), store the *events* that led there (Deposit $50, Withdraw $20, Deposit $70).
*   Allows time-travel debugging.

---

## 💻 Code Simulation: Event Bus

A simple Python implementation of the Observer pattern to simulate an Event Bus.

```python
class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data):
        print(f"📣 BROKER: Broadcasting '{event_type}'")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)

# --- The Services ---

def email_service(data):
    print(f"   📧 Email Service: Sending welcome email to {data['username']}")

def analytics_service(data):
    print(f"   📊 Analytics Service: Logging signup for {data['username']}")

def shipping_service(data):
    print(f"   📦 Shipping Service: Preparing starter kit for {data['username']}")

# --- Simulation ---

if __name__ == "__main__":
    bus = EventBus()

    # 1. Services subscribe to 'USER_SIGNUP'
    # Note: The 'Signup Service' doesn't know these exist.
    bus.subscribe("USER_SIGNUP", email_service)
    bus.subscribe("USER_SIGNUP", analytics_service)
    bus.subscribe("USER_SIGNUP", shipping_service)

    # 2. A User Signs up
    user_data = {"username": "john_doe", "id": 101}
    bus.publish("USER_SIGNUP", user_data)
```

**Output:**
```
📣 BROKER: Broadcasting 'USER_SIGNUP'
   📧 Email Service: Sending welcome email to john_doe
   📊 Analytics Service: Logging signup for john_doe
   📦 Shipping Service: Preparing starter kit for john_doe
```

---

## ⚠️ The Trap: "Event Hell" (Pinball Machine Architecture)
*   **Trap**: Chains of events. A triggers B, B triggers C, C triggers A (Loop!).
*   **Issue**: Extremely hard to debug. "Why did this user get a refund?"
*   **The Fix**: Keep event chains short. Use a **correlation_id** attached to the event to trace it across the system.

---

## ⚡ Flashcards

1.  **What is the difference between Orchestration and Choreography?**
    *   Orchestration: Central coordinator (Conductor) tells services what to do.
    *   Choreography: Services react to events (Dancers) without a central boss.
2.  **What is "At-Least-Once" delivery?**
    *   The guarantee that a message will be delivered, but it *might* be delivered multiple times (Duplicates possible). The consumer must be Idempotent.
3.  **What is the "Outbox Pattern"?**
    *   Writing to the DB and sending an Event must be atomic. The Outbox pattern writes the event to a DB table *in the same transaction*, then a separate worker publishes it.
