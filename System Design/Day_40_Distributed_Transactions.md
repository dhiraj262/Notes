# Day 40: Distributed Transactions

## 🎯 Goal
Understand how to maintain data consistency across multiple microservices/databases.
**Focus**: The impossibility of ACID across services and the alternatives (2PC, Sagas).

---

## 🧩 Key Concepts

### 1. The Problem
In a Monolith, `BEGIN TRANSACTION ... COMMIT` is easy.
In Microservices, Service A writes to DB1, Service B writes to DB2. There is no magic "Global Commit".
If Service A commits but Service B fails, data is inconsistent.

### 2. Two-Phase Commit (2PC) - The "Strong" Way
*   **Coordinator**: A central node asks everyone "Can you commit?"
*   **Phase 1 (Prepare)**: Coordinator asks A and B. They lock rows and vote "Yes".
*   **Phase 2 (Commit)**: If all Yes, Coordinator says "Commit". If any No, "Abort".
*   **Pros**: Strong Consistency (ACID).
*   **Cons**:
    *   **Blocking**: Everyone waits. Locks held for a long time.
    *   **SPOF**: If Coordinator dies, everyone is stuck.
    *   **Performance**: Very slow. Avoid in high-scale systems.

### 3. Sagas - The "Eventual" Way
*   **Concept**: Break a long transaction into a sequence of local transactions.
*   **Compensation**: If Step 3 fails, run "Compensating Transactions" to undo Step 2 and Step 1.
    *   *Example*: `Book Hotel` -> `Book Flight` -> `Charge Card`.
    *   *Failure*: Card Declined.
    *   *Compensation*: `Refund Flight` -> `Cancel Hotel`.
*   **Types**:
    *   **Choreography**: Events trigger next steps (No central boss).
    *   **Orchestration**: A central "Saga Coordinator" tells services what to do.

---

## 💻 Code Simulation: Saga (Orchestration)

Simulating a Travel Booking Saga where the final Payment step fails, triggering a rollback.

```python
# Simulation of a Saga Orchestrator

class Service:
    def __init__(self, name):
        self.name = name

    def execute(self, txn_id):
        # In real life, this is an API call
        print(f"✅ {self.name}: Reserved/Committed for {txn_id}")
        return True

    def compensate(self, txn_id):
        # The 'Undo' operation
        print(f"↩️ {self.name}: Canceled/Refunded {txn_id}")

class PaymentService(Service):
    def execute(self, txn_id):
        print(f"❌ {self.name}: Failed (Insufficient Funds) for {txn_id}")
        return False # Triggers rollback

class SagaOrchestrator:
    def __init__(self):
        self.steps = [] # List of {service, done_flag}

    def add_step(self, service):
        self.steps.append({"service": service, "done": False})

    def run(self, txn_id):
        print(f"--- Starting Saga {txn_id} ---")
        success = True

        # 1. Forward Phase
        for step in self.steps:
            service = step["service"]
            if service.execute(txn_id):
                step["done"] = True
            else:
                success = False
                break # Stop and rollback

        if success:
            print("🎉 Saga Complete!")
        else:
            print("⚠️ Failure detected! Starting Compensation...")
            self.rollback(txn_id)

    def rollback(self, txn_id):
        # 2. Backward Phase (Compensate in reverse order)
        for step in reversed(self.steps):
            if step["done"]:
                step["service"].compensate(txn_id)

if __name__ == "__main__":
    # Setup
    hotel = Service("Hotel")
    flight = Service("Flight")
    payment = PaymentService("Payment") # This one fails

    saga = SagaOrchestrator()
    saga.add_step(hotel)
    saga.add_step(flight)
    saga.add_step(payment)

    saga.run("TRIP-999")
```

**Output:**
```
--- Starting Saga TRIP-999 ---
✅ Hotel: Reserved/Committed for TRIP-999
✅ Flight: Reserved/Committed for TRIP-999
❌ Payment: Failed (Insufficient Funds) for TRIP-999
⚠️ Failure detected! Starting Compensation...
↩️ Flight: Canceled/Refunded TRIP-999
↩️ Hotel: Canceled/Refunded TRIP-999
```

---

## ⚠️ The Trap: "I need 2PC for Payments"
*   **Trap**: Thinking you need ACID for everything.
*   **Reality**: Even banks use Sagas (Eventual Consistency). If a transfer fails, they issue a "Reversing Entry" (Compensation). They don't lock the whole world.
*   **Exception**: Inside a *single* database (e.g., deducting balance and adding entry), ACID is fine. Across banks, it's Sagas.

---

## ⚡ Flashcards

1.  **What is the main drawback of 2PC?**
    *   It is a blocking protocol. If one participant is slow, everyone waits.
2.  **What is a "Pivot Transaction" in a Saga?**
    *   The point of no return. Steps before it can be compensated. Steps after it should be retriable (guaranteed to succeed).
3.  **Choreography vs Orchestration?**
    *   Choreography is decentralized (good for simple flows). Orchestration is centralized (good for complex flows with many steps).
