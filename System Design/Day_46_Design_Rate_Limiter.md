# Day 46: Design a Rate Limiter (Distributed)

## 🎯 Goal
Design a system to limit the number of requests a user can send to an API within a time window (e.g., 10 req/sec).
**Focus**: Algorithms, Distributed Counting (Redis), and Race Conditions.

---

## 🗣️ Requirements

### Functional
1.  **Limit Rule**: Limit requests based on different metrics (User ID, IP Address, API Key).
2.  **Configurability**: Different limits for different endpoints (e.g., `/login`: 5 req/min, `/search`: 100 req/min).
3.  **Feedback**: Return `429 Too Many Requests` when blocked.

### Non-Functional
1.  **Low Latency**: The check must be super fast (< 20ms).
2.  **Accuracy**: Strict enforcement is not always needed, but should be close.
3.  **Scalability**: Handle millions of counters.

---

## 🧠 Core Algorithms

### 1. Token Bucket
*   **Concept**: A bucket holds `N` tokens. Refills at `R` tokens/sec.
*   **Pros**: Memory efficient, allows **bursts** (if bucket is full).
*   **Cons**: Slightly complex to implement distributively.

### 2. Leaky Bucket
*   **Concept**: Requests enter a queue. Processed at constant rate. Overflow is dropped.
*   **Pros**: Smooths out traffic (no bursts).
*   **Cons**: Bursts are lost/delayed.

### 3. Fixed Window Counter
*   **Concept**: Count requests in `12:00-12:01`. Reset at `12:01`.
*   **Problem**: **Edge Case Spike**. If I send 10 reqs at `12:00:59` and 10 at `12:01:01`, I sent 20 requests in 2 seconds, violating a 10 req/min limit.

### 4. Sliding Window Log / Counter
*   **Concept**: Tracks timestamps or weighted counts to solve the edge case.
*   **Decision**: **Sliding Window Counter** (Redis Sorted Sets or Approximation) is often best for strictness, but **Token Bucket** is standard for API limiting.

---

## 🏗️ System Architecture

1.  **Middleware / API Gateway**:
    *   Intercepts every request.
    *   Extracts `API_Key` or `IP`.
    *   Asks **Rate Limiter Service** (or Redis directly): "Can I proceed?"
2.  **Redis (The Counter Store)**:
    *   In-memory, atomic increments.
    *   Use **Lua Scripts** to ensure atomicity (Check + Decrement in one go).
3.  **Configuration Service**:
    *   Stores rules (`/login` -> 5/min). Pushes updates to Rate Limiters.

---

## 💻 Code Simulation: Token Bucket Logic

Implementing the classic Token Bucket algorithm (in-memory simulation).

```python
import time
import threading

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate # tokens per second
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        if new_tokens > 0:
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

    def allow_request(self, tokens_needed=1):
        with self.lock:
            self._refill()
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            else:
                return False

if __name__ == "__main__":
    # Capacity 5, Refill 1 per sec
    bucket = TokenBucket(capacity=5, refill_rate=1)

    print("🚀 Bursting 5 requests...")
    for i in range(1, 8):
        allowed = bucket.allow_request()
        status = "✅ Allowed" if allowed else "⛔ Denied"
        print(f"Request {i}: {status} (Tokens left: {bucket.tokens:.2f})")
        time.sleep(0.1) # Fast requests

    print("\n⏳ Waiting 3 seconds...")
    time.sleep(3)

    print("🚀 Retrying...")
    if bucket.allow_request():
        print(f"Request 8: ✅ Allowed (Tokens left: {bucket.tokens:.2f})")
    else:
        print("Request 8: ⛔ Denied")
```

**Output:**
```
🚀 Bursting 5 requests...
Request 1: ✅ Allowed (Tokens left: 4.00)
...
Request 6: ⛔ Denied (Tokens left: 0.50)
...
🚀 Retrying...
Request 8: ✅ Allowed (Tokens left: 3.50)
```

---

## 🧠 Interview Nuances

### 1. How to handle Race Conditions in Distributed Env?
*   **Problem**: Two servers read `tokens=1`. Both decrement. Both allow request. `tokens` becomes `-1`.
*   **Solution**: **Redis Lua Script**.
    *   Executes `GET`, `CALCULATE`, `SET` as a single atomic operation in Redis.

### 2. Memory Optimization?
*   Storing `timestamp` for every request (Sliding Window Log) consumes too much RAM.
*   Use **Fixed Window** or **Token Bucket** (store just 2 integers: `count`, `last_refill`).

### 3. Client Side Throttling?
*   If server returns 429, client should handle it gracefully using **Exponential Backoff** and Jitter.

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem in rate limiting?**
    *   When many users retry exactly when the window resets. (Solved by adding 'jitter' to reset times).
2.  **Why use Redis for Rate Limiting?**
    *   Extremely fast (in-memory), supports atomic operations (INCR, Lua), and TTL (Time To Live).
3.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows bursts. Leaky Bucket forces constant rate.
