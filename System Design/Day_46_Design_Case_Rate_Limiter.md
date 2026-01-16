# Day 46: Design a Rate Limiter (Distributed)

## 🎯 Goal
Design a Distributed Rate Limiter service that throttles traffic based on IP, User ID, or API Key to prevent abuse and ensure system stability.

## 📋 Requirements

### Functional
1.  **Granularity**: Limit by User ID, IP, or Global.
2.  **Configurable Rules**: E.g., "5 req/sec" or "1000 req/day".
3.  **Feedback**: Return `429 Too Many Requests` with `Retry-After` header.

### Non-Functional
1.  **Low Latency**: The check must add minimal overhead (< 20ms).
2.  **Distributed**: Limits must apply across a cluster of servers (Global State).
3.  **Accuracy vs Performance**: Slight inaccuracies are acceptable for performance.
4.  **Fault Tolerance**: If the limiter fails, default to "Allow" (fail-open) to avoid blocking legitimate users.

## 🔢 Capacity Estimation

*   **Traffic**: 1 Million req/sec (Very high throughput).
*   **State**: Needs to track counts for millions of users.
*   **Memory**:
    *   If using Token Bucket, we need ~2 integers per user (Tokens, Timestamp).
    *   Size ~ 20 bytes/user.
    *   100M active users -> 2GB RAM (Fits easily in Redis).

## 🏗️ Architecture Design

### 1. Where to place it?
*   **Client Side**: Unreliable (can be forged).
*   **API Gateway (Middleware)**: Best place. Intercepts requests before hitting backend services.

### 2. Algorithms
1.  **Token Bucket**: Amazon/Stripe standard. Tokens added at rate $r$. Consume token to proceed.
    *   *Pros*: Allows bursts. Memory efficient.
2.  **Leaky Bucket**: Queue based. Outflow is constant.
    *   *Pros*: Smooths traffic. *Cons*: Drops bursts.
3.  **Fixed Window Counter**: Count requests in `12:00:00 - 12:00:01`.
    *   *Cons*: Spike at window edges (2x rate possible).
4.  **Sliding Window Log**: Stores timestamps. Extremely accurate but high memory cost.
5.  **Sliding Window Counter**: Hybrid. Approximates using weighted average of previous and current window.

### 3. Distributed State (Redis + Lua)
To enforce limits across multiple gateway nodes, we need a shared store.
*   **Redis**: In-memory, atomic increments (`INCR`).
*   **Race Conditions**:
    *   *Read-Modify-Write* is dangerous.
    *   **Solution**: Use **Lua Scripts** to execute the "Get -> Check -> Decrement" logic atomically inside Redis.

## 🐍 Code Simulation
Python simulation of **Token Bucket** (Burst capable) and **Sliding Window Counter** (Smoother).

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

    def allow_request(self, tokens_needed=1):
        with self.lock:
            self._refill()
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                print(f"[Allowed] Tokens left: {self.tokens:.2f}")
                return True
            else:
                print(f"[Blocked] Not enough tokens. Available: {self.tokens:.2f}")
                return False

    def _refill(self):
        now = time.time()
        delta = now - self.last_refill_timestamp
        tokens_to_add = delta * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_timestamp = now

class SlidingWindowCounter:
    """
    Simulates a window-based counter.
    In a real distributed system, 'redis_mock' would be actual Redis keys.
    """
    def __init__(self, window_size_seconds, limit):
        self.window_size = window_size_seconds
        self.limit = limit
        self.redis_mock = {}

    def allow_request(self):
        now = int(time.time())
        window_start = now - self.window_size

        # 1. Cleanup old keys (Simulates TTL in Redis)
        keys_to_delete = [k for k in self.redis_mock if k <= window_start]
        for k in keys_to_delete:
            del self.redis_mock[k]

        # 2. Count requests in current window
        total = sum(self.redis_mock.values())

        if total < self.limit:
            self.redis_mock[now] = self.redis_mock.get(now, 0) + 1
            print(f"[Allowed] Total in window: {total + 1}/{self.limit}")
            return True
        else:
            print(f"[Blocked] Limit reached: {total}/{self.limit}")
            return False

# --- Driver Code ---
if __name__ == "__main__":
    print("--- Token Bucket Test (Cap=2, Rate=1/sec) ---")
    bucket = TokenBucket(capacity=2, refill_rate=1)
    bucket.allow_request() # Allowed
    bucket.allow_request() # Allowed
    bucket.allow_request() # Blocked (Empty)
    time.sleep(1.1)        # Wait for refill
    bucket.allow_request() # Allowed

    print("\n--- Sliding Window Test (Limit=2 per 2 sec) ---")
    window = SlidingWindowCounter(window_size_seconds=2, limit=2)
    window.allow_request() # Allowed
    window.allow_request() # Allowed
    window.allow_request() # Blocked
```

## 🧠 Interview Nuances

### "The Trap": Simple INCR in Redis
*   **Problem**: Using `INCR` followed by `EXPIRE` is not atomic. If `EXPIRE` fails, the key persists forever.
*   **Solution**: Use Lua scripts or Redis transactions (`MULTI`/`EXEC`) to ensure atomicity.

### "The Kill Shot": Synchronization Issues
*   **Challenge**: "How do you handle rate limiting if the Redis cluster is overwhelmed?"
*   **Solution**: **Local Caching**. Store a small portion of the limit (e.g., 10%) in the application server's memory. If Redis is down/slow, use the local limiter. Or use **Probabilistic Limiting**.

### "Production Realities"
*   **Headers**: Always return `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset` so well-behaved clients can back off voluntarily.
*   **Noise**: Bot traffic can consume all tokens, blocking real users if they share an IP (NAT). Rate limit by API Key or User ID whenever possible, fallback to IP only for anonymous traffic.

## ⚡ Flashcards
*   **Best Algorithm for API?** -> Token Bucket (Allows bursts, low memory).
*   **Atomic Redis Op?** -> Lua Script.
*   **HTTP Code?** -> 429 Too Many Requests.
*   **Fail Strategy?** -> Fail-Open (Allow traffic if limiter breaks).
