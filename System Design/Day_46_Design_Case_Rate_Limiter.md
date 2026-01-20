# Day 46: Design Case - Distributed Rate Limiter

## 🎯 Goal
Design a Rate Limiter middleware to prevent abuse and protect downstream services.
**Focus**: Algorithms (Token Bucket), Distributed State (Redis), and Latency.

---

## 🗣️ Requirements

### Functional
1.  **Throttling**: Limit requests based on various rules (User ID, IP, API Key).
    *   e.g., "Max 10 requests per second per user".
2.  **Configurable**: Easy to change limits on the fly.
3.  **Response**: Return HTTP 429 (Too Many Requests) when blocked.

### Non-Functional
1.  **Low Latency**: < 20ms overhead.
2.  **Scalable**: Handle 1M+ RPS across multiple servers.
3.  **Accuracy**: Loose consistency is okay, but shouldn't be wildly off.

---

## 🧠 Core Design Decisions

### 1. Where to run it?
*   **Client Side**: Unreliable (can be forged).
*   **API Gateway (Middleware)**: Best place. Intercepts before hitting business logic.

### 2. Algorithms
*   **Token Bucket**: Good for bursty traffic. (Amazon uses this).
*   **Leaky Bucket**: Smooths out traffic (constant rate).
*   **Fixed Window**: Simple, but suffers from "edge case" spikes (2x traffic at minute boundary).
*   **Sliding Window Log**: Precise, but memory expensive (stores timestamp of every request).
*   **Sliding Window Counter**: Balanced approach.
    *   **Decision**: **Token Bucket** is standard for general API limiting.

### 3. Distributed State
*   If we have 10 API Servers, they need a shared counter.
*   **Redis**: Fast, in-memory, supports atomic operations.
*   **Race Conditions**: Reading count, incrementing, and saving is NOT atomic.
    *   **Solution**: **Lua Scripts** in Redis (executes atomically on the server side).

---

## 🏗️ System Architecture

1.  **Client** sends request.
2.  **API Gateway** (Nginx/Envoy/Custom Java Service).
3.  Gateway calculates a key: `ratelimit:{user_id}:{endpoint}`.
4.  Gateway runs **Lua Script** on Redis:
    *   "Get tokens".
    *   "If tokens > 0, decrement and allow".
    *   "Else, return 0 (block)".
5.  If Allowed: Forward to Backend Service.
6.  If Blocked: Return HTTP 429.

---

## 💻 Code Simulation: Token Bucket Algorithm

Implementing the logic in Python to understand how refill works.

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
        new_tokens = delta * self.refill_rate
        if new_tokens > 0:
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

    def allow_request(self, tokens=1):
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

if __name__ == "__main__":
    # Capacity 5, Refill 1 per sec
    limiter = TokenBucket(capacity=5, refill_rate=1)

    print("--- Burst of 5 requests ---")
    for i in range(5):
        allowed = limiter.allow_request()
        print(f"Req {i+1}: {'✅ Allowed' if allowed else '⛔ Blocked'}")

    print("--- 6th Request (Should Fail) ---")
    print(f"Req 6: {'✅ Allowed' if limiter.allow_request() else '⛔ Blocked'}")

    print("--- Waiting 2 seconds (Refill 2 tokens) ---")
    time.sleep(2)

    print(f"Req 7: {'✅ Allowed' if limiter.allow_request() else '⛔ Blocked'}")
    print(f"Req 8: {'✅ Allowed' if limiter.allow_request() else '⛔ Blocked'}")
    print(f"Req 9: {'✅ Allowed' if limiter.allow_request() else '⛔ Blocked'}")
```

**Output:**
```
--- Burst of 5 requests ---
Req 1: ✅ Allowed
Req 2: ✅ Allowed
Req 3: ✅ Allowed
Req 4: ✅ Allowed
Req 5: ✅ Allowed
--- 6th Request (Should Fail) ---
Req 6: ⛔ Blocked
--- Waiting 2 seconds (Refill 2 tokens) ---
Req 7: ✅ Allowed
Req 8: ✅ Allowed
Req 9: ⛔ Blocked
```

---

## 🧠 Interview Nuances

### 1. Redis is slow? (Network RTT)
*   Even Redis takes 1-2ms.
*   **Optimization**: Use local memory cache (Guava) for very hot keys (e.g., DDOS protection).
    *   Sync local cache with Redis asynchronously.
    *   Trade-off: Precision is lower (Total limit might exceed slightly).

### 2. Hard vs Soft Throttling
*   **Hard**: Reject immediately.
*   **Soft**: Allow but log, or serve degraded content.

### 3. Headers
*   Always return headers so clients can back off:
    *   `X-Ratelimit-Limit`: 100
    *   `X-Ratelimit-Remaining`: 0
    *   `X-Ratelimit-Retry-After`: 58s

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem?**
    *   When many clients retry simultaneously after a blackout, crushing the system again. Solution: Jitter (Randomize retry intervals).
2.  **Why use Lua with Redis?**
    *   To make read-modify-write operations atomic without using slow locks.
3.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows bursts (good for user interaction). Leaky Bucket enforces constant rate (good for packet switching/network).
