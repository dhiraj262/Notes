# Day 46: Design Case - Distributed Rate Limiter

## 🎯 Goal
Design a Rate Limiter to prevent abuse and ensure fair usage (e.g., 100 requests/minute per user).

---

## 🗣️ Requirements

### Functional
1.  **Throttling**: Limit requests based on defined rules (User ID, IP, API Key).
2.  **Configurable**: Different limits for different APIs (e.g., Write: 10/sec, Read: 1000/sec).
3.  **Feedback**: Return `429 Too Many Requests` with `Retry-After` header.

### Non-Functional
1.  **Low Latency**: Decision must be made in < 20ms.
2.  **Distributed**: Must work across a cluster of API servers.
3.  **Accuracy**: Should be reasonably accurate (strict locking not required, but don't allow double the limit).

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million.
*   **Requests**: 10 Billion/day.
*   **Peak**: ~150k requests/sec.
*   **Storage**: Need to store counters. Redis is essential for speed.

---

## 🧠 Core Design Decisions

### 1. Where to place it?
*   **Client Side**: Unreliable (can be forged).
*   **API Gateway**: Best place. Centralized control (Kong, Nginx).
*   **App Server**: Good for complex logic, but wastes resources if request is rejected late.
*   **Decision**: **API Gateway** (or a dedicated Middleware).

### 2. Algorithm Selection
*   **Fixed Window**: Reset counter every minute. Problem: Spike at edges (2x limit possible).
*   **Sliding Window Log**: Store timestamp of every request. Accurate but high memory cost.
*   **Token Bucket**: Tokens refill at rate `r`. flexible (allows bursts).
*   **Leaky Bucket**: Queue processes at constant rate. Smooths out traffic (good for write APIs).
*   **Decision**: **Token Bucket** (Standard for APIs) or **Sliding Window Counter** (Approximation).

### 3. Storage
*   Database is too slow.
*   **Redis** is perfect. Supports atomic increments (`INCR`) and Expiry (`EXPIRE`).

---

## 🏗️ System Architecture

1.  **Client** sends request.
2.  **Load Balancer** routes to API Gateway.
3.  **Rate Limiter Middleware**:
    *   Constructs Key: `ratelimit:{user_id}:{endpoint}`.
    *   Fetches current bucket state from **Redis**.
    *   If Tokens > 0: Decrement and Forward.
    *   If Tokens = 0: Return `429`.
4.  **Race Conditions**:
    *   Two servers read "Tokens = 1" at the same time. Both decrement.
    *   **Fix**: Use **Lua Scripts** in Redis to make "Read-Check-Decrement" atomic.

---

## 💻 Code Simulation: Token Bucket Algorithm

A Python implementation of the Token Bucket algorithm (In-Memory).

```python
import time
import threading

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate # tokens per second
        self.last_refill_timestamp = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        time_passed = now - self.last_refill_timestamp
        new_tokens = time_passed * self.refill_rate

        if new_tokens > 0:
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill_timestamp = now

    def allow_request(self, tokens_needed=1):
        with self.lock:
            self._refill()
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            else:
                return False

# Simulation Usage
if __name__ == "__main__":
    # Capacity 5, Refill 1 token/sec
    bucket = TokenBucket(capacity=5, refill_rate=1)

    print("🚀 Starting Burst traffic...")
    # Simulate burst of 10 requests
    for i in range(1, 11):
        allowed = bucket.allow_request()
        status = "✅ Passed" if allowed else "⛔ Rate Limited"
        print(f"Request {i}: {status} (Tokens left: {bucket.tokens:.2f})")
        time.sleep(0.1)

    print("\n⏳ Waiting 3 seconds for refill...")
    time.sleep(3)

    print("🚀 Retrying...")
    if bucket.allow_request():
        print(f"Request 11: ✅ Passed (Tokens left: {bucket.tokens:.2f})")
```

---

## 🧠 Interview Nuances

### 1. How to handle Distributed Race Conditions?
*   Problem: Read-Modify-Write cycle in Redis is not atomic.
*   Solution: **Redis Lua Script**.
    ```lua
    -- Lua script for Token Bucket
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    local tokens = tonumber(redis.call("get", key) or capacity)
    local last_refill = tonumber(redis.call("get", key.."_ts") or now)

    local delta = math.max(0, now - last_refill) * rate
    tokens = math.min(capacity, tokens + delta)

    if tokens >= 1 then
        redis.call("set", key, tokens - 1)
        redis.call("set", key.."_ts", now)
        return 1 -- Allowed
    else
        redis.call("set", key.."_ts", now)
        return 0 -- Rejected
    end
    ```

### 2. Soft vs Hard Rate Limiting?
*   **Hard**: Strict cutoff.
*   **Soft**: Allow short bursts over limit, or serve degraded content.

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem in Rate Limiting?**
    *   When many users get rate-limited and all retry at the exact same second (e.g., when the minute rolls over). Solution: Add **Jitter** (random delay) to retries.
2.  **Why use Lua with Redis?**
    *   Lua scripts execute atomically on the Redis server, preventing race conditions between checking a value and updating it.
3.  **Token Bucket vs Leaky Bucket?**
    *   **Token**: Allows bursts (good for user interaction).
    *   **Leaky**: Enforces constant rate (good for protecting DBs/Queues).
