# Day 46: Design a Rate Limiter (Distributed)

## 🎯 Goal
Design a distributed rate limiter to prevent abuse and protect downstream services from being overwhelmed.
**Focus**: Algorithms (Token Bucket), Distributed State (Redis), and Atomicity (Lua Scripts).

---

## 🗣️ Requirements

### Functional
1.  **Throttling**: Limit users to `X` requests per `Y` seconds (e.g., 10 req/min).
2.  **Granularity**: Support limits by User ID, IP Address, or API Key.
3.  **Feedback**: Return `429 Too Many Requests` with `Retry-After` header.

### Non-Functional
1.  **Low Latency**: < 20ms overhead added to request.
2.  **Accuracy**: Must be reasonably accurate across distributed servers.
3.  **Scalability**: Handle 100M+ requests/day.

---

## 📐 Capacity Estimation
*   **Total Traffic**: 1 Billion req/day -> ~12k req/sec.
*   **Read/Write**: Every request triggers a read and write to the rate limiter (Heavy Write Load).
*   **Storage**: Key: `user_id`, Value: `counter` (Int). Small storage footprint. Redis is perfect.

---

## 🧠 Core Design Decisions

### 1. Where to place the Limiter?
*   **Client Side**: Unreliable (can be forged).
*   **Application Code**: Hard to scale, coupled with business logic.
*   **API Gateway (Middleware)**: **Best**. Centralized control, protects backend services.

### 2. Algorithms
*   **Fixed Window**: Reset counter every minute. *Issue*: Spike at edges of window (2x traffic allowed).
*   **Sliding Window Log**: Store timestamp of every request. *Issue*: High memory usage.
*   **Token Bucket**: Bucket fills with tokens at rate `r`. Request consumes token. *Pros*: Allows bursts, memory efficient.
*   **Decision**: **Token Bucket** or **Sliding Window Counter**.

### 3. Distributed State Challenge
*   If we use local memory in the API Gateway, user requests hitting different servers won't share the limit.
*   **Solution**: **Redis** as a centralized store.
*   **Race Condition**: Two servers read `count=9` at same time, both increment to `10`.
*   **Fix**: **Lua Scripts** in Redis to ensure `GET + INCR` happens atomically.

---

## 🏗️ System Architecture

1.  **Client**: Sends request.
2.  **Load Balancer**: Routes to API Gateway.
3.  **API Gateway (Middleware)**:
    *   Extracts User ID.
    *   Calls **Redis** (via Lua Script) to check limit.
    *   If `Allowed`: Forward to Backend Service.
    *   If `Blocked`: Return HTTP 429.
4.  **Backend Service**: Processes business logic.

---

## 💻 Code Simulation: Token Bucket

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
        # Add tokens based on time passed
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
if __name__ == "__main__":
    # Capacity 5, Refill 1 token/sec
    limiter = TokenBucket(capacity=5, refill_rate=1)

    print("🚀 Sending 10 requests quickly...")
    for i in range(1, 11):
        if limiter.allow_request():
            print(f"Request {i}: ✅ Allowed")
        else:
            print(f"Request {i}: ⛔ Throttled")
        time.sleep(0.1) # Fast requests

    print("\n😴 Sleeping for 3 seconds...")
    time.sleep(3)

    print("🚀 Sending request after wait...")
    if limiter.allow_request():
        print(f"Request 11: ✅ Allowed")
```

**Output:**
```
🚀 Sending 10 requests quickly...
Request 1: ✅ Allowed
Request 2: ✅ Allowed
Request 3: ✅ Allowed
Request 4: ✅ Allowed
Request 5: ✅ Allowed
Request 6: ⛔ Throttled
Request 7: ⛔ Throttled
...
😴 Sleeping for 3 seconds...
🚀 Sending request after wait...
Request 11: ✅ Allowed
```

---

## 🧠 Interview Nuances

### 1. Hard vs Soft Throttling?
*   **Hard**: Immediately reject.
*   **Soft**: Allow briefly (burst) but slow down subsequent requests (Traffic Shaping).

### 2. Distributed Race Conditions?
*   Explain the **Redis Lua Script** approach.
*   `eval "local current = redis.call('get', KEYS[1])..."` executes as a single atomic operation in Redis single thread.

### 3. How to handle different tiers (Free vs Paid)?
*   Store rules in a config DB/Cache.
*   `get_limit(user_id)` -> returns 10 for Free, 100 for Paid.
*   Pass this limit to the Token Bucket logic.

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem?**
    *   When many clients retry simultaneously after a service comes back up. Rate Limiters help mitigate this.
2.  **Why use Redis for Rate Limiting?**
    *   It's an in-memory store (extremely fast) and supports atomic operations (INCR, Lua), which are essential for counting requests accurately.
3.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows bursts of traffic. Leaky Bucket enforces a constant output rate (smooths traffic).
