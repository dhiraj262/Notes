# 🛑 Interview Post-Mortem: "I Bombed Rate Limiting"

> **Context**: This is a breakdown of a common System Design interview failure mode: knowing the *algorithms* (Token Bucket, Leaky Bucket) but failing the *justification* (Magic Numbers) and *implementation details* (Concurrency).

---

## 1. The Trap: "Where did you get that number?"

**The Scenario**: You draw a Redis instance and a Token Bucket diagram. You confidently say, *"I'll set the limit to 100 requests per minute."*

**The Kill Shot**: The interviewer asks, *"Why 100? Why not 1000? What if your user is a mobile app that makes 50 requests on startup?"*

**The Failure**: You guessed. You treated the number as a configuration detail rather than a design constraint.

### ✅ The Fix: Back-of-the-Envelope Estimation
Never pull a number out of thin air. Derive it from business metrics.

**Formula**:
$$ \text{Avg TPS} = \frac{\text{DAU} \times \text{Reqs/User}}{\text{Seconds in Day (86,400)}} $$

**Example Calculation**:
1.  **DAU**: 10 Million users.
2.  **Usage**: Average user opens app 5 times/day. Each open = 10 API calls. Total = 50 reqs/user/day.
3.  **Total Requests**: $10M \times 50 = 500M$ reqs/day.
4.  **Avg TPS**: $500,000,000 / 86,400 \approx 5,800$ TPS.
5.  **Peak TPS**: Traffic isn't flat. Assume standard 5x multiplier. $5,800 \times 5 \approx 29,000$ TPS.

**Justification**: *"I'm designing for a peak load of ~30k TPS. A per-user limit of 100 RPM seems low for a bursty mobile app, so I'll design a **Token Bucket** which allows bursts, rather than a strict Fixed Window."*

---

## 2. Algorithm Selection: "Use the Right Tool"

| Algorithm | Pros | Cons | Best For |
| :--- | :--- | :--- | :--- |
| **Fixed Window** | Simple, Memory efficient (1 counter). | **Edge Burst**: Can allow 2x limit at window boundary. | Low-tier APIs where strictness doesn't matter. |
| **Sliding Window Log** | Perfect accuracy. | **Expensive**: Stores timestamp of *every* request. | High-security APIs (e.g., Failed Logins). |
| **Token Bucket** | Allows **Bursts** (good for mobile). Memory efficient. | Complex to implement distributed (race conditions). | General purpose user APIs. |

---

## 3. The Implementation: Python + Redis + Lua

**The Challenge**: In a distributed system, reading a counter and writing it back is **not atomic**.
*   **Race Condition**: Two requests read "99" at the same time. Both increment to "100". Both pass. Real count is 101.
*   **Solution**: Use **Lua Scripts** in Redis to ensure atomicity (Redis is single-threaded).

### 🐍 Code: Sliding Window Log (Strict Mode)

This implementation is "expensive" (O(N) memory) but perfect for interviews to show you understand correctness.

```python
import time
import redis

class SlidingWindowLimiter:
    def __init__(self, redis_client, window_size_sec=60, limit=100):
        self.redis = redis_client
        self.window = window_size_sec
        self.limit = limit

    def is_allowed(self, user_id):
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - self.window

        # LUA SCRIPT: Atomic Execution
        # 1. Remove old timestamps (ZREMRANGEBYSCORE)
        # 2. Count remaining (ZCARD)
        # 3. If count < limit, add new timestamp (ZADD)
        # 4. Set expiry (EXPIRE)
        lua_script = """
        local key = KEYS[1]
        local window_start = tonumber(ARGV[1])
        local now = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local window_size = tonumber(ARGV[4])

        -- Remove requests older than the window
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

        -- Count current requests
        local current_count = redis.call('ZCARD', key)

        if current_count < limit then
            -- Allowed: Add current timestamp
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window_size + 1)
            return 1 -- True
        else
            return 0 -- False
        end
        """

        # Register and execute script
        cmd = self.redis.register_script(lua_script)
        result = cmd(keys=[key], args=[window_start, now, self.limit, self.window])

        return bool(result)

# Usage
r = redis.Redis(host='localhost', port=6379, db=0)
limiter = SlidingWindowLimiter(r, window_size_sec=60, limit=5)

for i in range(7):
    print(f"Request {i+1}: {'Allowed' if limiter.is_allowed('user_123') else 'Blocked'}")
```

---

## 4. Production Realities (The "Senior" Section)

If you pass the coding part, they will grill you on "Hard Mode" scenarios.

### A. The "Thundering Herd" after Reset
*   **Problem**: If 1 million users all have their counters reset at 12:00:00, your database will melt at 12:00:01.
*   **Fix**: **Jitter**. Add random variance to the window expiration.
    *   *Bad*: `limit_reset = 60s`
    *   *Good*: `limit_reset = 60s + random(0, 5)s`

### B. Distributed Clock Skew
*   **Problem**: Server A thinks it's 10:00:01. Server B thinks it's 10:00:02. They calculate different window starts.
*   **Fix**: Rely on **Redis Time** (Centralized Time) or use a logic that relies on relative TTLs, not absolute timestamps.

### C. Client Side: "Please Retry"
*   **Problem**: A blocked client immediately retries in a tight loop, worsening the outage.
*   **Fix**: Return `Retry-After` header. Client **must** use **Exponential Backoff** (wait 1s, 2s, 4s, 8s...).

---

## 🧠 Flashcards

1.  **Q: Why is Fixed Window dangerous?**
    *   *A: It allows 2x traffic at the edge of the window (e.g., 100 reqs at 10:59 and 100 reqs at 11:01).*
2.  **Q: How do you handle a bursty mobile app?**
    *   *A: Use Token Bucket (allows bursts up to bucket size) instead of Sliding Window.*
3.  **Q: Why use Lua in Redis?**
    *   *A: To make multiple operations (Read -> Check -> Write) atomic and prevent race conditions.*
4.  **Q: What is the complexity of Sliding Window Log?**
    *   *A: High memory usage O(N) where N is requests per window. Not suitable for high-throughput (DDoS protection).*
