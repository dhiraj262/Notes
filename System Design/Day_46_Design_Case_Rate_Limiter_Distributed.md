# Day 46: Design Case - Distributed Rate Limiter

## 🎯 Goal
Design a scalable, distributed rate limiter to prevent abuse and ensure fair usage of APIs.
**Focus**: Algorithms, Race Conditions, and Redis.

---

## 🗣️ Requirements

### Functional
1.  **Throttling**: Limit users to X requests per Y seconds (e.g., 10 reqs/sec).
2.  **Distributed**: Works across multiple servers (stateless API servers).
3.  **Granularity**: Support different limits for different APIs (e.g., `POST /order` vs `GET /status`).

### Non-Functional
1.  **Low Latency**: The check must be fast (< 10ms).
2.  **Accuracy**: Reasonable accuracy (allow small drift, but no huge breaches).
3.  **High Availability**: If Rate Limiter fails, should we Block or Allow? (Fail-Open usually).

---

## 📐 Capacity Estimation
*   **Scale**: 100 Million requests/day.
*   **Peak**: 50,000 requests/sec.
*   **Memory**: If we track 1M active users, and each key is 100 bytes.
    *   1M * 100 bytes = 100 MB (Easily fits in Redis).

---

## 🧠 Core Design Decisions

### 1. Where to store state?
*   **Local Memory**: Fast, but doesn't work for distributed servers (User might hit Server A then Server B).
*   **Database (SQL)**: Too slow (disk I/O).
*   **Cache (Redis)**: **Perfect**. In-memory, supports atomic operations (`INCR`, `Lua`).

### 2. Algorithms
*   **Token Bucket**: Good for burstiness. Hard to implement distributedly without race conditions.
*   **Fixed Window Counter**: Simple (`INCR key:time`). **Problem**: "Edge case" (2x traffic at boundary).
*   **Sliding Window Log**: Stores every timestamp. **Accurate** but expensive (high memory).
*   **Sliding Window Counter**: Hybrid. Best of both worlds.

### 3. Handling Race Conditions
*   **Problem**: Read-Modify-Write is not atomic.
    *   Thread A reads count = 9.
    *   Thread B reads count = 9.
    *   Both increment to 10. Actual count = 11.
*   **Solution**: **Redis Lua Script**. Redis guarantees the script executes atomically.

---

## 🏗️ System Architecture

1.  **Client**: Sends request.
2.  **API Gateway / Middleware**: Intercepts request.
3.  **Rate Limiter Service**:
    *   Constructs key: `ratelimit:{user_id}:{api_endpoint}`.
    *   Calls Redis.
4.  **Redis**: Executes Lua script. Returns `1` (Allow) or `0` (Block).
5.  **API Gateway**:
    *   If Allow: Pass to Backend.
    *   If Block: Return `HTTP 429 Too Many Requests`.

---

## 💻 Code Simulation: Fixed Window with Redis

Simulating a Fixed Window Counter approach. Ideally, we would use Lua, but here we simulate the logic.

```python
import time

class RedisMock:
    def __init__(self):
        self.store = {} # key -> {value, expiry}

    def incr(self, key):
        if key not in self.store:
            self.store[key] = {'val': 0, 'exp': None}
        self.store[key]['val'] += 1
        return self.store[key]['val']

    def expire(self, key, seconds):
        if key in self.store:
            self.store[key]['exp'] = time.time() + seconds

    def cleanup(self):
        # Lazy expiration simulation
        now = time.time()
        keys = list(self.store.keys())
        for k in keys:
            if self.store[k]['exp'] and self.store[k]['exp'] < now:
                del self.store[k]

class RateLimiter:
    def __init__(self, limit, window_sec):
        self.redis = RedisMock()
        self.limit = limit
        self.window = window_sec

    def is_allowed(self, user_id):
        self.redis.cleanup()

        # Key depends on the current time window
        # e.g., timestamp 100 -> window 100 (if window=1)
        # timestamp 101 -> window 101
        current_window = int(time.time() / self.window)
        key = f"{user_id}:{current_window}"

        count = self.redis.incr(key)

        if count == 1:
            # First request in this window, set expiry
            self.redis.expire(key, self.window + 1)

        if count > self.limit:
            print(f"⛔ Blocked: User {user_id} (Count: {count})")
            return False

        print(f"✅ Allowed: User {user_id} (Count: {count})")
        return True

if __name__ == "__main__":
    # Limit: 2 requests per second
    limiter = RateLimiter(limit=2, window_sec=1)

    limiter.is_allowed("user_1") # 1
    limiter.is_allowed("user_1") # 2
    limiter.is_allowed("user_1") # 3 (Block)

    print("⏳ Waiting 1.1s...")
    time.sleep(1.1)

    limiter.is_allowed("user_1") # 1 (Reset)
```

**Output:**
```
✅ Allowed: User user_1 (Count: 1)
✅ Allowed: User user_1 (Count: 2)
⛔ Blocked: User user_1 (Count: 3)
⏳ Waiting 1.1s...
✅ Allowed: User user_1 (Count: 1)
```

---

## 🧠 Interview Nuances

### 1. Hard vs Soft Rate Limiting
*   **Hard**: Strict rejection.
*   **Soft**: Allow but log, or serve stale data/downgraded response.

### 2. Different Levels
*   **User Level**: Prevent one user spamming.
*   **IP Level**: Prevent DDoS.
*   **Global Level**: Protect the database from total collapse.

### 3. Headers
*   Return standard headers so clients can back off:
    *   `X-RateLimit-Limit`: 100
    *   `X-RateLimit-Remaining`: 0
    *   `X-RateLimit-Reset`: 1609459200

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem?**
    *   When many clients retry simultaneously after a rate limit resets. Fix: Add Jitter (random noise) to the backoff.
2.  **Why use Lua with Redis?**
    *   To ensure **Atomicity**. Multiple commands (`GET`, `INCR`) run as a single transaction, preventing race conditions.
3.  **Token Bucket vs Leaky Bucket?**
    *   **Token Bucket**: Allows bursts (if tokens exist).
    *   **Leaky Bucket**: Smooths traffic to a constant rate (queue processing).
