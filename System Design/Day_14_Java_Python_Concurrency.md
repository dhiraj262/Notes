# Day 14: Java & Python Concurrency Deep Dive

## 🎯 Goal
Move from theory to practice. Understand how the two most popular backend languages handle concurrency. Learn about the GIL, Futures, and Virtual Threads.

---

## 🐍 Python Concurrency: The GIL

### What is the GIL?
**Global Interpreter Lock (GIL)** is a mutex that allows only one thread to hold control of the Python interpreter.
*   **Result**: CPU-bound multi-threading in Python is **single-core**. You get concurrency (context switching), but not true parallelism.

### Workarounds
1.  **Multiprocessing**: Use `multiprocessing` module to spawn separate **Processes** (each has its own Python interpreter and GIL).
    *   *Best for*: CPU-intensive tasks (Image processing, ML).
2.  **AsyncIO**: Cooperative multitasking (Single thread, Event loop).
    *   *Best for*: I/O-intensive tasks (Web requests, DB queries).

---

## ☕ Java Concurrency: The Powerhouse

Java threads map 1:1 to Kernel threads. They are heavy but powerful.

### 1. The Executor Framework
Don't manage `new Thread()` manually. Use **Executors**.
*   `FixedThreadPool(n)`: Good for predictable load.
*   `CachedThreadPool()`: Spawns threads as needed. Dangerous (can OOM).
*   `ScheduledThreadPool()`: For recurring tasks.

### 2. CompletableFuture (Java 8+)
The standard for asynchronous programming in Java.
*   **Chaining**: `.thenApply()`, `.thenAccept()`.
*   **Combining**: `CompletableFuture.allOf(f1, f2)`.

```java
CompletableFuture.supplyAsync(() -> fetchUserData(userId))
    .thenCombine(
        CompletableFuture.supplyAsync(() -> fetchUserOrders(userId)),
        (user, orders) -> new UserDashboard(user, orders)
    )
    .thenAccept(dashboard -> sendToClient(dashboard));
```

### 3. Virtual Threads (Java 21 / Project Loom)
*   **Problem**: Kernel threads are expensive (1MB stack). You can only have ~10k threads.
*   **Solution**: **Virtual Threads**. Managed by the JVM, not OS. Cheap. You can have millions.
*   **Impact**: Makes blocking code (Synchronous) as efficient as Async code.

---

## ⚖️ Comparative Analysis

| Feature | Python (CPython) | Java (JVM) |
| :--- | :--- | :--- |
| **Threading Model** | 1:1 (OS Thread), but limited by GIL | 1:1 (OS Thread) |
| **Parallelism** | No (for CPU tasks) | Yes (Multicore) |
| **I/O Concurrency** | Excellent (Async/Await) | Excellent (Threads / NIO / Virtual Threads) |
| **Stack Size** | Variable | Large (~1MB default) |
| **Best Use** | Scripting, ML Glue, Simple Web Servers | High-Scale Enterprise Systems, Kafka Consumers |

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| Does **Python** support true parallelism? | Not with threads (due to GIL). Yes with `multiprocessing`. |
| What is a **Daemon Thread** in Java? | A low-priority thread that runs in the background (e.g., GC). The JVM exits if only Daemon threads are left. |
| What is `volatile` in Java? | A keyword that guarantees **visibility**. Reads/Writes go directly to main memory, skipping CPU cache. It does NOT guarantee atomicity. |
| What is the benefit of **Virtual Threads**? | They decouple the "Task" from the "OS Thread". Allows writing simple blocking code that scales like async code. |

---

## 🛠️ Practical Task
**Task**: Implement a **Rate Limiter Client** (Client-side throttling).
*   **Language**: Choose Java or Python.
*   **Scenario**: You need to call an API 100 times, but it only allows 5 requests/second.
*   **Implementation**:
    1.  Create a `Task` that prints "Request sent at {time}".
    2.  Use a `ScheduledExecutorService` (Java) or `asyncio` with `sleep` (Python).
    3.  Ensure the tasks are spaced out correctly.
