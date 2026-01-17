# Day 46: Design Case - Distributed Rate Limiter

## 🎯 Goal
Design a system to limit the number of API requests a user can make within a time window (e.g., 10 requests per second).
**Focus**: Accuracy, Performance, and Distributed coordination.

---

## 🗣️ Requirements

### Functional
1.  **Throttling**: Block requests exceeding the limit.
2.  **Granularity**: User-level (UserID), IP-level, or Global.
3.  **Feedback**: Return HTTP 429 (Too Many Requests).

### Non-Functional
1.  **Low Latency**: Decision must be < 5ms.
2.  **Distributed**: Works across multiple API servers.
3.  **Accuracy**: Flexible tolerance (10% over-limit is okay for some systems).

---

## 📐 Capacity Estimation
*   **Traffic**: 1 Million TPS (Global).
*   **Redis Ops**: Each request needs a check. Redis must handle 1M OPS.
    *   Need Redis Cluster or Sharding.
*   **Memory**: Simple counters.
    *   Key: `user_123`, Value: `int`. 100 bytes.
    *   100M active users -> 10GB RAM (Manageable).

---

## 🧠 Core Design Decisions

### 1. Where to run?
*   **Client-side**: Unreliable (can be forged).
*   **Application Server**: Hard to sync between servers.
*   **Middleware/API Gateway**: **Best**. Centralized control (Nginx, Kong, or custom service).

### 2. Algorithms
*   **Token Bucket**: Good for burst traffic. (Used by Amazon).
*   **Leaky Bucket**: Smooths out traffic. (Used by Shopify).
*   **Fixed Window Counter**: Simple, but has "Edge Case" issues (double limit at window boundary).
*   **Sliding Window Log**: Very accurate, high memory cost.
*   **Sliding Window Counter**: Best balance of accuracy and memory.

### 3. Distributed State
*   **Redis**: Standard choice. Fast in-memory counter.
*   **Race Conditions**: Two servers read counter=9 at same time, both increment to 10. Actual=11.
    *   **Solution**: **Lua Script** in Redis (Atomic execution).
    *   `EVAL "local current = redis.call('incr', key); if current > limit then return 0 else return 1 end"`

---

## 🏗️ System Architecture

1.  **Client** sends request.
2.  **Load Balancer** forwards to **API Gateway**.
3.  **Rate Limiter Middleware** (in Gateway):
    *   Constructs Key: `ratelimit:{user_id}`.
    *   Calls Redis (Cluster) via Lua Script.
4.  **Redis**: Returns `ALLOWED` or `DENIED`.
5.  **Gateway**:
    *   If `ALLOWED`: Forwards to Service.
    *   If `DENIED`: Returns HTTP 429.

---

## 💻 Code Simulation: Token Bucket Algorithm

A Python implementation of the Token Bucket algorithm (in-memory version). In production, this logic moves to Redis.

```python
import time
import threading

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity      # Max tokens
        self.tokens = capacity        # Current tokens
        self.refill_rate = refill_rate # Tokens per second
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        # Add tokens based on time passed
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
            return False

if __name__ == "__main__":
    # Capacity 5, Refill 1 per sec
    limiter = TokenBucket(capacity=5, refill_rate=1)

    print("Request 1-5 (Should Pass):")
    for i in range(5):
        print(f"Req {i+1}: {'✅ Pass' if limiter.allow_request() else '❌ Fail'}")

    print("Request 6 (Should Fail):")
    print(f"Req 6: {'✅ Pass' if limiter.allow_request() else '❌ Fail'}")

    print("Waiting 2 seconds...")
    time.sleep(2)

    print("Request 7-8 (Should Pass):")
    for i in range(2):
        print(f"Req {7+i}: {'✅ Pass' if limiter.allow_request() else '❌ Fail'}")
```

**Output:**
```
Request 1-5 (Should Pass):
Req 1: ✅ Pass
Req 2: ✅ Pass
Req 3: ✅ Pass
Req 4: ✅ Pass
Req 5: ✅ Pass
Request 6 (Should Fail):
Req 6: ❌ Fail
Waiting 2 seconds...
Request 7-8 (Should Pass):
Req 7: ✅ Pass
Req 8: ✅ Pass
```

---

## 🧠 Interview Nuances

### 1. Hard vs Soft Rate Limiting?
*   **Hard**: Strict rejection.
*   **Soft**: Allow overload for short time, or degrade quality (e.g., return cached data).

### 2. Header Standards?
*   `X-Ratelimit-Limit`: 100
*   `X-Ratelimit-Remaining`: 20
*   `X-Ratelimit-Retry-After`: 5s

### 3. Synchronization Issues?
*   In a multi-region setup, syncing Redis across regions is too slow.
*   **Solution**: Localize rate limits (e.g., 100 total = 50 US + 50 EU), or use loose consistency.

---

## ⚡ Flashcards
1.  **Why use Lua Scripts for Rate Limiting?**
    *   To ensure atomicity. Reading, Incrementing, and Checking must happen as a single operation to prevent race conditions.
2.  **What is the "Thundering Herd" problem in Rate Limiting?**
    *   If many users retry exactly when the window resets. Solution: Add "Jitter" (random noise) to the reset time.
3.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows bursts (if tokens exist). Leaky Bucket enforces a constant output rate (smooths traffic).
