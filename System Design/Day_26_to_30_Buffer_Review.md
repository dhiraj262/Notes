# Day 26-30: Buffer & Review - Foundations

## 🎯 Goal
Consolidate knowledge from the first 25 days. Focus on strengthening the "Foundations" before moving to Distributed Systems.
**Focus**: Reviewing OOD Patterns, Concurrency, and Database Internals.

---

## 📚 Key Concepts Review

### 1. Object-Oriented Design (Days 1-7)
*   **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
*   **Patterns**:
    *   *Creational*: Singleton (One instance), Factory (Object creation logic).
    *   *Structural*: Adapter (Wrapper), Decorator (Add behavior dynamically).
    *   *Behavioral*: Observer (Pub/Sub), Strategy (Swap algorithms), State (Finite State Machine).
*   **LLD**: Parking Lot, Elevator. Focus on Interface definition and separation of concerns.

### 2. Concurrency (Days 8-14)
*   **Process vs Thread**: Process = Layout (Heap/Stack). Thread = Execution Unit (Stack).
*   **Locks**: Mutex (Mutual Exclusion), Semaphores (Count based).
*   **Deadlocks**: 4 Conditions (Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait).
*   **Java/Python**: ThreadPoolExecutor, GIL (Python Global Interpreter Lock).

### 3. Database Internals (Days 15-20)
*   **Storage**:
    *   **LSM Trees** (Write optimized, Sequential I/O) -> Cassandra, Kafka.
    *   **B-Trees** (Read optimized, Block based) -> MySQL, Postgres.
*   **Indexing**: Hash Index (Key-Value), Bloom Filters (Probabilistic "Might exist").
*   **Transactions**: ACID. Isolation Levels (Read Uncommitted -> Serializable).
*   **NoSQL**:
    *   *Key-Value*: Redis.
    *   *Document*: MongoDB.
    *   *Columnar*: Cassandra.
    *   *Graph*: Neo4j.

---

## 🛠️ Practical Tasks (Buffer Period)

### Task 1: Read DDIA
*   Finish **Chapter 3** (Storage & Retrieval).
*   Start **Chapter 5** (Replication) to prep for next week.

### Task 2: Mini-Project (CLI Tool)
*   Build a simple **Thread-Safe Key-Value Store** in Java or Python.
    *   Support `put(k, v)` and `get(k)`.
    *   Use `ReadWriteLock` to allow multiple readers but one writer.
    *   Persist data to a file (simple Append-Only Log).

---

## 💻 Code Simulation: Thread-Safe Cache

```python
import threading
import time

class ThreadSafeCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock() # Or RLock

    def put(self, key, value):
        with self._lock:
            print(f"🔒 Writing {key}: {value}")
            self._cache[key] = value
            time.sleep(0.1) # Simulate IO

    def get(self, key):
        with self._lock:
            val = self._cache.get(key)
            print(f"🔓 Reading {key}: {val}")
            return val

def writer(cache):
    for i in range(5):
        cache.put(f"key{i}", i)

def reader(cache):
    for i in range(5):
        cache.get(f"key{i}")

if __name__ == "__main__":
    cache = ThreadSafeCache()
    t1 = threading.Thread(target=writer, args=(cache,))
    t2 = threading.Thread(target=reader, args=(cache,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
```

---

## ⚡ Flashcards
1.  **Difference between Strategy and State pattern?**
    *   Strategy: Client passes the algorithm (behavior). State: Object changes its own behavior based on internal state.
2.  **Why are LSM Trees faster for writes?**
    *   They append to a log (Sequential I/O) instead of jumping around disk pages (Random I/O like B-Trees).
3.  **What is the ABA problem?**
    *   In CAS (Compare-And-Swap), a value changes from A -> B -> A. A thread thinks it hasn't changed, but it has. Solved with version numbers.
