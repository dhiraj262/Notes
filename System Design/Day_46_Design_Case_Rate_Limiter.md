# Day 46: Design Case - Distributed Rate Limiter

## 🎯 Goal
Design a Rate Limiter to protect APIs from abuse (DDoS) and ensure fair usage.
**Focus**: Accuracy, Low Latency, and Distributed Consistency.

---

## 🗣️ Requirements

### Functional
1.  **Rules**: Allow 10 requests/sec per user.
2.  **Scope**: Global (Distributed across multiple servers).
3.  **Response**: Return `429 Too Many Requests` when limit exceeded.

### Non-Functional
1.  **Low Latency**: < 20ms added overhead per request.
2.  **High Availability**: The limiter itself shouldn't become a SPOF.
3.  **Accuracy**: Should be reasonably accurate (strict locking not always required).

---

## 📐 Capacity Estimation
*   **API Traffic**: 1 Million req/sec.
*   **Rate Limiter Ops**: 1 Million ops/sec (every request checks the limiter).
*   **Redis ops**: Redis can handle ~100k ops/sec per instance. Need a cluster.

---

## 🏗️ System Architecture

### 1. Where to place it?
*   **Client Side**: Unreliable (can be forged).
*   **Server Side**: Deep integration, but couples logic.
*   **Middleware/API Gateway (Preferred)**: Centralized control (Nginx, Kong, or custom service).

### 2. Algorithms
1.  **Token Bucket**: (Most common). Tokens added at rate `r`. Request consumes token.
2.  **Leaky Bucket**: Fixed output rate. Good for smoothing bursts.
3.  **Fixed Window**: Reset counter every minute. Problem: Spike at edges (e.g., 59s and 01s).
4.  **Sliding Window Log**: Stores timestamps. Accurate but high memory.
5.  **Sliding Window Counter**: Hybrid. Approx average of previous window + current.

### 3. Distributed Implementation (Redis)
*   **Problem**: Race conditions.
    *   Thread A reads counter = 9.
    *   Thread B reads counter = 9.
    *   Both increment to 10. Actual is 11.
*   **Solution**: **Lua Scripts**.
    *   Lua scripts execute atomically in Redis.
    *   Perform "Get, Check, Decrement" in one step.

---

## 💻 Code Simulation: Token Bucket

Simulating the **Token Bucket** algorithm logic.

```python
import time

class RateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate # tokens per second
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        delta = now - self.last_refill
        tokens_to_add = delta * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def allow_request(self, tokens=1):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            print(f"✅ Allowed. Tokens left: {self.tokens:.2f}")
            return True
        else:
            print(f"⛔ Denied. Tokens left: {self.tokens:.2f}")
            return False

if __name__ == "__main__":
    # Capacity 5, Refill 1 per second
    limiter = RateLimiter(capacity=5, refill_rate=1)

    print("--- Burst of 5 ---")
    for i in range(5):
        limiter.allow_request()

    print("--- 6th Request (Should fail) ---")
    limiter.allow_request()

    print("--- Wait 2 seconds ---")
    time.sleep(2)

    print("--- Retry ---")
    limiter.allow_request()
```

**Output:**
```
--- Burst of 5 ---
✅ Allowed. Tokens left: 4.00
✅ Allowed. Tokens left: 3.00
✅ Allowed. Tokens left: 2.00
✅ Allowed. Tokens left: 1.00
✅ Allowed. Tokens left: 0.00
--- 6th Request (Should fail) ---
⛔ Denied. Tokens left: 0.00
--- Wait 2 seconds ---
--- Retry ---
✅ Allowed. Tokens left: 1.00
```

---

## 🧠 Interview Nuances

### 1. Hard vs Soft Rate Limiting?
*   **Hard**: Strict rejection. (DDoS protection).
*   **Soft**: Allow short bursts, but throttle later.

### 2. How to handle many users?
*   Memory optimization.
*   Don't store keys for inactive users. Set TTL on Redis keys.

### 3. Client handling?
*   Return HTTP Headers:
    *   `X-Ratelimit-Limit`: 100
    *   `X-Ratelimit-Remaining`: 5
    *   `X-Ratelimit-Retry-After`: 60

---

## ⚡ Flashcards
1.  **Why Lua in Redis?**
    *   To ensure atomicity of multiple operations (Read-Update-Write) without using heavy locks.
2.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows bursts (if tokens available). Leaky Bucket enforces constant output rate (no bursts).
3.  **What is Thundering Herd?**
    *   When many processes wake up for an event, or when a cache expires. Not directly rate limiting, but rate limiting prevents the herd from crashing the DB.
