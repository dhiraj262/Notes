# 🤝 System Design Deep Dive: Distributed Transactions

> **Context**: Ensuring data consistency across Microservices. Why Two-Phase Commit (2PC) hurts availability and how the Saga Pattern (Orchestration) solves it using Compensating Transactions.

---

## 1. The Trap: "Two-Phase Commit (2PC)"

**The Scenario**: You are designing an E-commerce system.
*   **Order Service**: Creates an order.
*   **Inventory Service**: Reserves items.
*   **Payment Service**: Charges the card.

The interviewer asks: *"How do we ensure that if Payment fails, we release the Inventory and Cancel the Order?"*

**The Amateur Answer**: *"I'll use a Distributed Transaction with Two-Phase Commit (XA Standard)."*

**The Kill Shot**: *"Okay, so while the Payment Service is processing (which takes 3 seconds), the Inventory row is **locked** by the database coordinator. If the Payment Coordinator crashes, the Inventory is locked **indefinitely**. How does this scale to 10,000 TPS?"*

**The Failure**: 2PC is a **Blocking Protocol**. It reduces the availability of your entire system to the availability of the slowest component.

---

## 2. The Solution: The Saga Pattern

**Concept**: Break the global transaction into a sequence of **Local Transactions**. If one fails, execute a series of **Compensating Transactions** (Undo steps) to roll back the changes.

**Styles**:
1.  **Choreography**: Services emit events ("OrderCreated" -> Inventory listens). Hard to debug at scale.
2.  **Orchestration**: A central "Saga Orchestrator" (State Machine) commands each service. Easier to manage.

---

## 3. The Implementation: Python Saga Orchestrator

**The logic**: We define a list of `steps`. Each step has an `execute` function and a `compensate` function.

```python
import logging

# Mock Services
class InventoryService:
    def reserve(self, item_id):
        print(f"📦 Inventory: Reserved {item_id}")
        return True
    def release(self, item_id):
        print(f"📦 Inventory: Released {item_id}")

class PaymentService:
    def charge(self, amount):
        print(f"💳 Payment: Charging ${amount}...")
        # Simulate Failure
        if amount > 1000:
            print("💳 Payment: ❌ Declined (Over limit)")
            return False
        print("💳 Payment: ✅ Success")
        return True
    def refund(self, amount):
        print(f"💳 Payment: Refunded ${amount}")

# Saga Orchestrator
class SagaOrchestrator:
    def __init__(self):
        self.steps = []
        self.executed_steps = []

    def add_step(self, execute_func, compensate_func, name):
        self.steps.append({
            "execute": execute_func,
            "compensate": compensate_func,
            "name": name
        })

    def run(self):
        print("--- Starting Saga ---")
        for step in self.steps:
            try:
                success = step["execute"]()
                if success:
                    self.executed_steps.append(step)
                else:
                    print(f"🚨 Step '{step['name']}' Failed! Triggering Rollback...")
                    self.rollback()
                    return False
            except Exception as e:
                print(f"🚨 Exception in '{step['name']}': {e}. Triggering Rollback...")
                self.rollback()
                return False

        print("--- Saga Completed Successfully ---")
        return True

    def rollback(self):
        print("--- ↩️ Starting Compensation ---")
        # Reverse order
        for step in reversed(self.executed_steps):
            print(f"↩️ Compensating '{step['name']}'...")
            step["compensate"]()
        print("--- Compensation Complete ---")

# --- Simulation ---
inventory = InventoryService()
payment = PaymentService()
saga = SagaOrchestrator()

# Transaction: Buy Item #55 for $1500 (Will Fail Payment)
item_id = 55
amount = 1500

# Step 1: Inventory
saga.add_step(
    execute_func=lambda: inventory.reserve(item_id),
    compensate_func=lambda: inventory.release(item_id),
    name="Reserve Inventory"
)

# Step 2: Payment
saga.add_step(
    execute_func=lambda: payment.charge(amount),
    compensate_func=lambda: payment.refund(amount), # technically not needed if charge failed, but good for partials
    name="Process Payment"
)

# Run
saga.run()
```

---

## 4. Production Realities (The "Senior" Section)

### A. Idempotency is Mandatory
*   **Scenario**: The Orchestrator sends "Charge" to Payment. Payment succeeds, but the network crashes before the Ack returns. Orchestrator thinks it failed and retries.
*   **Risk**: Double Charge.
*   **Fix**: Every step must be Idempotent. Use an `idempotency_key` (e.g., Order ID) to ensure the operation happens exactly once.

### B. "Zombie" Sagas
*   **Scenario**: The Orchestrator crashes in the middle of a transaction.
*   **Fix**: Persist the State Machine to a database (e.g., Redis/SQL). On startup, read pending Sagas and resume/rollback them.

### C. Isolation (The "I" in ACID)
*   **Problem**: Sagas do **not** provide Isolation. User A reserves an item. User B sees the reserved item (Inventory count - 1). User A's payment fails and rolls back. User B acted on temporary data ("Dirty Read").
*   **Fix**: Semantic Locking (state = `PENDING`) or accepting Eventual Consistency trade-offs.

---

## 🧠 Flashcards

1.  **Q: Why is 2PC bad for Microservices?**
    *   *A: It holds database locks across services, creating a performance bottleneck and a Single Point of Failure (Coordinator).*
2.  **Q: What is the difference between Choreography and Orchestration?**
    *   *A: Choreography = Event-driven (Services talk to each other). Orchestration = Central Controller (Command-driven).*
3.  **Q: What happens if a Compensation step fails?**
    *   *A: Massive alert. Human intervention required. Retry indefinitely until success (Compensations must be safe/idempotent).*
4.  **Q: Does Saga guarantee ACID?**
    *   *A: No. It guarantees ACD (Atomicity via compensation, Consistency, Durability), but Isolation is sacrificed (Eventual Consistency).*
5.  **Q: What is a "Pivot Transaction" in a Saga?**
    *   *A: The step that, once successful, ensures the entire saga will complete. Steps before it are compensatable; steps after it must succeed (retryable).*
