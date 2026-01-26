# Day 26-30: Buffer & Review - Month 1 Foundations

## 🎯 Goal
Consolidate knowledge from the first 30 days. Review Object-Oriented Design, Concurrency, Database Internals, and Low-Level Design patterns.

---

## 🧠 Key Concept Summaries

### 1. Object-Oriented Design (OOD)
*   **SOLID Principles**:
    *   **S**ingle Responsibility: One reason to change.
    *   **O**pen/Closed: Open for extension, closed for modification.
    *   **L**iskov Substitution: Subtypes must be substitutable for base types.
    *   **I**nterface Segregation: Specific interfaces > General ones.
    *   **D**ependency Inversion: Depend on abstractions, not concretions.
*   **Design Patterns**:
    *   **Creational**: Singleton (One instance), Factory (Object creation logic), Builder (Complex objects).
    *   **Structural**: Adapter (Incompatible interfaces), Decorator (Add duties dynamically), Facade (Simplified interface).
    *   **Behavioral**: Observer (Pub/Sub), Strategy (Interchangeable algos), Command (Encapsulate request).

### 2. Concurrency & OS
*   **Process vs Thread**: Process = Isolated memory; Thread = Shared memory.
*   **Locks**: Mutex (Mutual Exclusion), Semaphores (Signaling).
*   **Deadlocks**: 4 conditions (Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait).
*   **Async**: Futures, Promises, CompletableFutures (Non-blocking I/O).

### 3. Database Internals
*   **Storage Engines**:
    *   **LSM Trees** (Log-Structured Merge): Fast Writes, Append-only (Cassandra, Kafka).
    *   **B-Trees**: Fast Reads, Update-in-place (PostgreSQL, MySQL).
*   **Indexing**: Bloom Filters (Probabilistic set membership), Hash Indexes.
*   **Transactions (ACID)**:
    *   **A**tomicity: All or nothing.
    *   **C**onsistency: Valid state.
    *   **I**solation: Concurrent txns don't interfere (Read Committed, Serializable).
    *   **D**urability: Persisted to disk.

### 4. Low-Level Design (LLD)
*   **Approach**: Requirements -> Class Diagram -> Interfaces -> Implementation.
*   **Key Problems**: Parking Lot, Elevator System, Task Scheduler.
*   **Code Quality**: DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid).

---

## ⚡ Flashcards

1.  **When to use NoSQL vs SQL?**
    *   **SQL**: Structured data, ACID required, Complex joins (Financial systems).
    *   **NoSQL**: Unstructured data, High throughput, Horizontal scaling (Social feeds, Logs).

2.  **What is the difference between Strategy and Factory pattern?**
    *   **Factory**: Creates objects (Creational).
    *   **Strategy**: Selects an algorithm at runtime (Behavioral).

3.  **Explain "Index" to a 5-year-old.**
    *   It's like the index at the back of a book. Instead of reading every page to find "Harry Potter", you go to the index, find the page number, and go straight there.

4.  **What is a Bloom Filter?**
    *   A space-efficient probabilistic data structure that tells you if an element is *definitely not* in the set or *maybe* in the set.

---

## 🛠️ Practical Activity (Month 1 Capstone)

**Task**: Build a simple **CLI Task Manager** in Python/Java.
*   **Features**: Add task, List tasks, Mark done, Delete task.
*   **Requirements**:
    *   Save data to a JSON file (Persistence).
    *   Use the **Command Pattern** for CLI actions.
    *   Use the **Singleton Pattern** for the Storage Manager.

```python
# Quick Skeleton for Command Pattern
class Command:
    def execute(self): pass

class AddTaskCommand(Command):
    def __init__(self, task): self.task = task
    def execute(self): print(f"Adding {self.task}")

class CLI:
    def __init__(self): self.commands = {}
    def register(self, name, command): self.commands[name] = command
    def run(self, cmd_name): self.commands.get(cmd_name).execute()
```
