# Day 38: Message Queues - Kafka vs RabbitMQ

## 🎯 Goal
Understand Asynchronous Messaging. Learn when to use a **Queue** (RabbitMQ) vs a **Log** (Kafka).
**Focus**: Decoupling services and handling spikes (Load Levelling).

---

## 🧩 Key Concepts

### 1. Why Message Queues?
*   **Decoupling**: Service A (Producer) doesn't need to know if Service B (Consumer) is online.
*   **Load Levelling**: If A sends 1000 reqs/sec but B can only handle 100, the Queue buffers the requests. B processes at its own pace.
*   **Reliability**: Messages are persisted. If B crashes, it resumes processing when it restarts.

### 2. RabbitMQ (Traditional Queue)
*   **Model**: "Smart Broker, Dumb Consumer".
*   **Mechanism**: Producer sends to Exchange -> Routes to Queue -> Consumer picks up.
*   **State**: Once a message is consumed (acked), it is **deleted** from the queue.
*   **Best For**: Complex routing, Job queues, Task processing.

### 3. Kafka (Distributed Log)
*   **Model**: "Dumb Broker, Smart Consumer".
*   **Mechanism**: A continuous append-only log file.
*   **State**: Messages are **retained** (e.g., for 7 days). Consumers track their own "Offset" (pointer).
*   **Best For**: High throughput events, Analytics, Replaying data (Event Sourcing).

---

## 📊 Comparison Table

| Feature | RabbitMQ (Queue) | Kafka (Log) |
| :--- | :--- | :--- |
| **Data Retention** | Deleted after consumption | Retained (Configurable) |
| **Throughput** | 4K-10K msgs/sec | 1 Million+ msgs/sec |
| **Delivery** | Push (usually) | Pull (Consumer polls) |
| **Priority** | Supports Priority Queues | No (Strict Ordering in Partition) |
| **Ordering** | No guarantee if multiple consumers | Strict Order within a Partition |
| **Use Case** | Background Jobs, Celery | Logs, Stream Processing |

---

## 💻 Code Simulation: Queue vs Log

Let's simulate the fundamental difference: RabbitMQ deletes tasks, Kafka allows multiple readers to see the same history.

```python
import queue
import threading

# 1. Traditional Queue (RabbitMQ Style)
# Messages are consumed and REMOVED.
def rabbitmq_simulation():
    q = queue.Queue()
    for i in range(3): q.put(f"Task {i}")

    print("--- RabbitMQ (Queue) ---")
    while not q.empty():
        msg = q.get()
        print(f"Worker consumed: {msg} (Gone from Queue)")

# 2. Log-Based (Kafka Style)
# Messages STAY. Different consumers read same data.
def kafka_simulation():
    log = [f"Event {i}" for i in range(3)]

    print("\n--- Kafka (Log) ---")
    # Consumer A (Analytics)
    for offset, msg in enumerate(log):
        print(f"Analytics Service read offset {offset}: {msg}")

    # Consumer B (Notifications) - Reads SAME data later
    for offset, msg in enumerate(log):
        print(f"Notification Service read offset {offset}: {msg}")

if __name__ == "__main__":
    rabbitmq_simulation()
    kafka_simulation()
```

**Output:**
```
--- RabbitMQ (Queue) ---
Worker consumed: Task 0 (Gone from Queue)
Worker consumed: Task 1 (Gone from Queue)
Worker consumed: Task 2 (Gone from Queue)

--- Kafka (Log) ---
Analytics Service read offset 0: Event 0
Analytics Service read offset 1: Event 1
Analytics Service read offset 2: Event 2
Notification Service read offset 0: Event 0
Notification Service read offset 1: Event 1
Notification Service read offset 2: Event 2
```

---

## ⚠️ The Trap: "Kafka is a Queue"
*   **Trap**: Treating Kafka like a job queue.
*   **Why**: In Kafka, partitions are hard to scale dynamically. In RabbitMQ, adding consumers is easy.
*   **The Fix**: Use Kafka for Data Pipelines (Events). Use RabbitMQ/SQS for Task Processing (Jobs).

---

## ⚡ Flashcards

1.  **What is a Dead Letter Queue (DLQ)?**
    *   A side queue where failed messages are sent after N retries, so they don't block the main processing.
2.  **What happens to message order in Kafka?**
    *   Ordering is guaranteed **only within a Partition**, not across the whole Topic.
3.  **What is "Backpressure"?**
    *   When the consumer tells the producer (or the system) to slow down because it's overwhelmed. RabbitMQ handles this well.
