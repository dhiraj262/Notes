# Day 8: Concurrency & Multithreading Basics

## 🎯 Goal
Understand the building blocks of high-throughput systems. LLD interviews often test if you know how to handle race conditions.

---

## 🧵 Process vs Thread
*   **Process**: An independent program in execution (e.g., Chrome, VSCode). Has its own memory space (Heap). Communication between processes (IPC) is expensive.
*   **Thread**: A lightweight unit of execution within a process. Threads share the same memory (Heap) but have their own Stack. Communication is cheap/fast.

---

## 🔒 The Problem: Race Conditions
When two threads try to modify the same variable at the same time, data corruption occurs.

**Example**:
*   `Counter = 0`
*   Thread A reads 0.
*   Thread B reads 0.
*   Thread A increments to 1, writes 1.
*   Thread B increments to 1, writes 1.
*   **Result**: 1 (Should be 2).

### The Solution: Synchronization
1.  **Locks / Mutex**: Only one thread can hold the lock. Others wait.
    *   Java: `synchronized` keyword, `ReentrantLock`.
    *   Python: `threading.Lock()`.
2.  **Atomic Variables**: Hardware-level support for atomic operations.
    *   Java: `AtomicInteger`.

---

## 🏊 Thread Pools
Creating a thread is expensive (OS overhead). Don't create a new thread for every request.
**Use a Thread Pool**: A collection of pre-created threads that sit idle, waiting for work.

*   **Java**: `ExecutorService`, `ThreadPoolExecutor`.
*   **Pattern**: Producer-Consumer.
    *   Task Queue holds tasks.
    *   Worker Threads pick tasks from Queue.

```java
// Java Example
ExecutorService executor = Executors.newFixedThreadPool(10); // 10 workers

for (int i = 0; i < 100; i++) {
    executor.submit(() -> {
        System.out.println("Processing task...");
    });
}
```

---

## 🛑 Deadlock
Occurs when two threads are stuck forever, waiting for each other to release a lock.
*   Thread A holds Lock 1, wants Lock 2.
*   Thread B holds Lock 2, wants Lock 1.
*   **Fix**: Always acquire locks in the same order (Hierarchy).

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| **Process** vs **Thread**: Main difference? | Threads share memory (Heap) within the same process. Processes have isolated memory. |
| What is a **Race Condition**? | When system behavior depends on the timing/sequence of threads, leading to bugs. |
| What is a **Context Switch**? | The CPU saving the state of the current thread and loading the state of the next thread. It is expensive. |
| How to prevent **Deadlock**? | Resource Ordering (Acquire Lock A, then B. Never B then A). |

---

## 🛠️ Practical Task
**Task**: Implement a **Thread-Safe Counter**.
1.  Create a class `Counter` with `increment()`.
2.  Spawn 100 threads, each incrementing it 1000 times.
3.  Ensure the final result is exactly 100,000.
4.  Try using `synchronized` first, then `AtomicInteger`.
