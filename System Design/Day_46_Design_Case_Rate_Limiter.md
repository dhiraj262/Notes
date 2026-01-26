# Day 46: Design Case - Rate Limiter (Distributed)

## 🎯 Goal
Design a distributed rate limiter to prevent abuse and ensure system stability.
**Focus**: Algorithms, Distributed Counting, Race Conditions.

---

## 🗣️ Requirements

### Functional
1.  **Throttle Requests**: Limit requests based on user_id, IP, or API key.
2.  **Flexible Rules**: "10 req/sec" or "1000 req/hour".
3.  **Feedback**: Return HTTP 429 (Too Many Requests) when blocked.

### Non-Functional
1.  **Low Latency**: The check must be fast (< 5ms).
2.  **Accuracy**: Distributed environment should be reasonably accurate.
3.  **High Availability**: The limiter itself shouldn't become a SPOF.
4.  **Scalability**: Handle 1M+ active users.

---

## 🧠 Core Design Decisions

### 1. Where to put the Rate Limiter?
*   **Client**: Unreliable. Easily forged.
*   **Server Code**: Hard to scale. Coupled with business logic.
*   **API Gateway (Middleware)**: **Best**. Centralized control (Nginx, Kong, or custom Microservice).

### 2. Algorithms
*   **Token Bucket**: Tokens refill at rate `r`. Take token to process. Good for bursts.
*   **Leaky Bucket**: Requests enter queue, processed at constant rate. Good for smoothing bursts.
*   **Fixed Window**: "100 reqs in 12:00-12:01". Problem: Spike at edges (200 reqs between 12:00:59 and 12:01:01).
*   **Sliding Window Log**: Store timestamp of every request. Exact but high memory cost.
*   **Sliding Window Counter**: Hybrid. Approximates count using previous window weight. **Best Balance**.

### 3. Distributed State Store: Redis
*   Need shared state for distributed servers.
*   **Redis**: In-memory, fast.
*   **Race Conditions**: Reading counter, incrementing, and writing back is not atomic.
*   **Solution**: Use **Lua Scripts** in Redis to make the `Check-and-Decrement` operation atomic.

---

## 🏗️ System Architecture

1.  **Client** sends request to **API Gateway**.
2.  **Rate Limiter Middleware** intercepts.
3.  **Redis** stores the counters (Key: `limiter:{user_id}`).
4.  **Lua Script** runs on Redis:
    *   Get current tokens.
    *   Refill based on time passed.
    *   If tokens > 0, decrement and allow.
    *   Else, deny.
5.  **Gateway**:
    *   If Allowed: Pass to Backend Service.
    *   If Denied: Return HTTP 429.

---

## 💻 Code Simulation: Token Bucket (Local)

Simulating the core logic of a Token Bucket algorithm.

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
        delta = now - self.last_refill
        tokens_to_add = delta * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def allow_request(self, tokens=1):
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

# Simulation
limiter = TokenBucket(capacity=5, refill_rate=1) # 1 token/sec, Burst 5

def user_request(user_id, delay=0):
    time.sleep(delay)
    if limiter.allow_request():
        print(f"✅ Request {user_id} Allowed (Tokens left: {limiter.tokens:.2f})")
    else:
        print(f"⛔ Request {user_id} Denied (Tokens left: {limiter.tokens:.2f})")

if __name__ == "__main__":
    print("--- Start Burst (5 allowed) ---")
    threads = []
    for i in range(7):
        t = threading.Thread(target=user_request, args=(i,))
        threads.append(t)
        t.start()

    for t in threads: t.join()

    print("\n--- Wait 2 seconds (Refill 2 tokens) ---")
    time.sleep(2)
    user_request(99)
```

**Output:**
```
--- Start Burst (5 allowed) ---
✅ Request 0 Allowed
✅ Request 1 Allowed
✅ Request 2 Allowed
✅ Request 3 Allowed
✅ Request 4 Allowed
⛔ Request 5 Denied
⛔ Request 6 Denied

--- Wait 2 seconds (Refill 2 tokens) ---
✅ Request 99 Allowed
```

---

## 🧠 Interview Nuances

### 1. Redis is down?
*   **Fail-Open**: Allow all requests. Better to overload backend slightly than block legitimate users.
*   **Fail-Closed**: Block all. High security but bad UX.
*   **Design Choice**: Usually Fail-Open for consumer apps.

### 2. Hard vs Soft Rate Limiting?
*   **Hard**: Strict cutoff.
*   **Soft**: Allow overload for short time (bursts).

### 3. Header Standardization
*   `X-Ratelimit-Limit`: 100
*   `X-Ratelimit-Remaining`: 99
*   `X-Ratelimit-Retry-After`: 60 (seconds)

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem?**
    *   Many clients retrying simultaneously after being rate-limited, causing another spike. Solution: Exponential Backoff + Jitter.
2.  **Why use Lua with Redis?**
    *   To ensure atomicity. Executing logic *inside* Redis prevents race conditions between `GET` and `SET`.
3.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows **Bursts** (up to capacity). Leaky Bucket enforces **Constant Rate**.
