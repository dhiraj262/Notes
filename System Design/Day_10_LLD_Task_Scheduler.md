# Day 10: LLD Practice - Task Scheduler

## 🎯 Goal
Design a system that schedules and executes tasks based on priority or time.
**Key Concepts**: PriorityQueue, Concurrency, Producer-Consumer.

---

## 🗣️ Requirements
1.  **Submit Task**: Users can submit a task with a `Priority` (High, Medium, Low) and an execution time.
2.  **Execution**: System should execute tasks. High priority first.
3.  **Recurring**: Support recurring tasks (e.g., "Run every 10 mins").
4.  **Concurrency**: Multiple workers executing tasks in parallel.

---

## 🏗️ Core Components

### 1. Task
```java
class Task implements Comparable<Task> {
    int id;
    int priority; // 0 = Critical, 10 = Low
    long scheduledTime;
    Runnable job;

    public int compareTo(Task other) {
        // Sort by Time first, then Priority
        if (this.scheduledTime != other.scheduledTime)
            return Long.compare(this.scheduledTime, other.scheduledTime);
        return Integer.compare(this.priority, other.priority);
    }
}
```

### 2. TaskScheduler (The Brain)
*   Uses a **Min-Heap** (`PriorityBlockingQueue` in Java) to store tasks.
*   Head of the queue is always the task that needs to run *soonest*.

```java
class TaskScheduler {
    PriorityBlockingQueue<Task> queue;

    public void schedule(Task t) {
        queue.add(t);
    }
}
```

### 3. Worker (The Muscle)
*   A thread that constantly checks the queue.
*   `take()`: Blocks if queue is empty.
*   If task time > current time: Wait/Sleep.

```java
class Worker implements Runnable {
    public void run() {
        while (true) {
            Task t = queue.peek();
            if (t.scheduledTime <= System.currentTimeMillis()) {
                queue.poll(); // Remove
                t.job.run();  // Execute
            } else {
                Thread.sleep(t.scheduledTime - now);
            }
        }
    }
}
```

---

## 🧠 Interview Nuances
1.  **How to handle "Recurring" tasks?**
    *   After execution, re-add the task to the queue with `newTime = currentTime + interval`.
2.  **What if the queue gets too big?**
    *   Persist tasks to a Database (Redis/SQL). Memory is volatile.
3.  **Dynamic Thread Pool?**
    *   If queue size grows, spawn more workers.

---

## 🛠️ Practical Task
Implement a **Cron Job Scheduler** in your favorite language using a Priority Queue.
*   Input: `schedule(Task, "at 10:00")`.
*   Output: Print "Running Task" at 10:00.
