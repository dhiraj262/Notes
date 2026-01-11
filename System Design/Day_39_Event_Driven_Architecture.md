# Day 39: Event-Driven Architecture (EDA)

## 🎯 Goal
Understand how to build systems where components communicate by reacting to events, leading to high decoupling and scalability.
**Focus**: Pub/Sub pattern, Choreography vs Orchestration, and Event sourcing.

---

## 🧩 Key Concepts

### 1. What is an Event?
*   A significant change in state (e.g., "OrderPlaced", "PaymentFailed").
*   **Fact**: Events are immutable. You cannot change what happened in the past.

### 2. Request-Driven vs Event-Driven
*   **Request-Driven (HTTP/REST)**: Synchronous. Service A calls Service B. A waits for B.
    *   *Pros*: Simple, easy to trace.
    *   *Cons*: Tight coupling. If B is down, A fails.
*   **Event-Driven (Pub/Sub)**: Asynchronous. Service A emits an event. Service B, C, D listen and react.
    *   *Pros*: Loose coupling. A doesn't know B exists.
    *   *Cons*: Complexity. Harder to debug flow.

### 3. Topologies
*   **Mediator (Orchestrator)**: A central "Brain" (e.g., Workflow Engine) receives events and tells services what to do.
*   **Broker (Choreography)**: No central brain. Services subscribe to events and decide what to do.

---

## 🏗️ Architecture Pattern: Event Sourcing
Instead of storing just the *current state* (e.g., "Balance: $50"), store the *sequence of events* that led to it.
*   Events: `Deposited $100` -> `Withdrew $20` -> `Withdrew $30`.
*   Current State: Replay all events -> $50.
*   **Pros**: Audit trail, time travel (debug past states).
*   **Cons**: Storage growth, need "Snapshots" to speed up replay.

---

## 💻 Code Simulation: Simple Event Bus

A Python implementation of the Observer Pattern (the core of EDA).

```python
class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data):
        print(f"📢 Publishing event: {event_type} with data: {data}")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)

# Services (Subscribers)
def send_welcome_email(user):
    print(f"📧 Sending welcome email to {user['name']}")

def add_to_analytics(user):
    print(f"📊 Logging new user {user['name']} to analytics")

# Usage
bus = EventBus()
bus.subscribe("UserSignedUp", send_welcome_email)
bus.subscribe("UserSignedUp", add_to_analytics)

# User signs up (Publisher)
new_user = {"id": 1, "name": "Alice"}
bus.publish("UserSignedUp", new_user)
```

---

## ⚠️ The Trap: Distributed Tracing
*   **Problem**: In EDA, a user request might trigger events across 10 microservices. If something fails, how do you find the root cause?
*   **The Fix**: **Correlation ID**.
    *   Generate a unique ID (Trace ID) at the entry point.
    *   Pass this ID in the metadata/headers of every event.
    *   Logs from all services can be aggregated (e.g., in ELK stack) and queried by this ID.

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem in Pub/Sub?**
    *   When many subscribers wake up simultaneously to process an event, causing a resource spike.
2.  **Difference between Message Queue and Event Bus?**
    *   **Queue**: Point-to-Point. Command-oriented ("Do this"). Data usually deleted after consumption.
    *   **Event Bus**: Pub/Sub. Fact-oriented ("This happened"). Data often persists for multiple listeners.
3.  **What is CQRS (Command Query Responsibility Segregation)?**
    *   Splitting the Read and Write models. Writes go to a normalized DB. Events replicate data to a specialized Read DB (e.g., ElasticSearch) optimized for queries.
