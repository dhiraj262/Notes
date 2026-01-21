# Day 46: Design Case - Rate Limiter (Distributed)

## 🎯 Goal
Design a distributed rate limiter to prevent abuse and protect services from being overwhelmed (DoS).
**Focus**: Algorithms, Race Conditions, and Low Latency.

---

## 🗣️ Requirements

### Functional
1.  **Limit Rules**: Configurable (e.g., 5 req/sec per user, 100 req/min per IP).
2.  **Response**: If allowed, pass. If blocked, return HTTP 429 (Too Many Requests).
3.  **Granularity**: User-level, IP-level, API-level.

### Non-Functional
1.  **Low Latency**: Must decide in < 10ms.
2.  **Accuracy**: Should not block valid traffic excessively.
3.  **Distributed**: Shared limits across multiple server instances.
4.  **Fault Tolerance**: If limiter fails, default to "Allow" (fail-open) to avoid outage.

---

## 📐 Capacity Estimation
*   **Throughput**: Checking the limit must be extremely fast. If API does 100k QPS, Limiter needs 100k QPS.
*   **Storage**: storing counters.
    *   100M Users.
    *   Counter = 4 bytes + Key (UserID) = 20 bytes.
    *   Total ~ 2GB (Fits in Redis Memory).

---

## 🧠 Core Design Decisions

### 1. Where to put it?
*   **Client**: Unreliable (can be forged).
*   **API Gateway**: Good central place.
*   **Sidecar**: Good for microservices (Mesh).
*   **Decision**: **Middleware/Redis** accessible by API Gateway.

### 2. Algorithms
*   **Token Bucket**: Tokens added at rate R. Request consumes token. (Bursty traffic allowed).
*   **Leaky Bucket**: Requests enter queue, processed at constant rate. (Smooths traffic).
*   **Fixed Window**: Counter resets every minute. (Spike at edge: 2x limit possible).
*   **Sliding Window Log**: Store timestamp of every request. (Accurate but expensive memory).
*   **Sliding Window Counter**: Hybrid. Approx count based on overlap.
*   **Decision**: **Token Bucket** (Standard) or **Sliding Window Counter** (Accurate & light).

### 3. Distributed State
*   **Local Memory**: Fast but limits are not shared (User can hit Server A 5 times + Server B 5 times).
*   **Central Redis**: Shared state.
    *   *Problem*: Race conditions (Read-Modify-Write).
    *   *Solution*: **Lua Scripts** in Redis (Atomic execution).

---

## 🏗️ System Architecture

1.  **Client** sends request.
2.  **Rate Limiter Middleware** intercepts.
3.  **Check Redis**:
    *   Run Lua script.
    *   Get `current_tokens` for `user_id`.
    *   If `tokens > 0`, decrement and `Allow`.
    *   Else `Deny`.
4.  **Forward**: If allowed, forward to API Server.

---

## 💻 Code Simulation: Token Bucket (In-Memory)

Simulating the logic of a Token Bucket.

```python
import time
import threading

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate # Tokens per second
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
            return False

if __name__ == "__main__":
    # Bucket: Max 10 tokens, Refills 1 token/sec
    limiter = TokenBucket(capacity=10, refill_rate=1)

    # Simulate bursts
    for i in range(12):
        allowed = limiter.allow_request()
        status = "✅ Allowed" if allowed else "⛔ Blocked"
        print(f"Req {i+1}: {status} | Tokens left: {int(limiter.tokens)}")
        time.sleep(0.1) # Fast requests

    print("Waiting 2 seconds...")
    time.sleep(2)

    print(f"Req 13: {'✅ Allowed' if limiter.allow_request() else '⛔ Blocked'}")
```

**Output:**
*   First 10 requests allowed.
*   11th, 12th blocked (Empty bucket).
*   After wait, bucket refills, 13th allowed.

---

## 🧠 Interview Nuances

### 1. Race Conditions in Distributed Environment?
*   Two servers read `count=4`. Both increment to 5. Actual requests = 6. Limit violated.
*   **Fix**: Redis `INCR` (Atomic) or Lua Script.
    *   Lua: `local current = redis.call('GET', key); if current < limit then redis.call('INCR', key); return 1; else return 0; end`

### 2. How to handle many users?
*   Memory optimization. If a user hasn't made a request in 1 hour, expire the key (TTL).

### 3. Hard vs Soft Rate Limiting?
*   Hard: Strict rejection.
*   Soft: Allow but log/alert (for short bursts).

---

## ⚡ Flashcards
1.  **What is the "Thundering Herd" problem?**
    *   When many processes wake up simultaneously to handle an event (e.g., cache expiry), overloading the system. Rate limiting helps.
2.  **Why use Lua in Redis?**
    *   It guarantees atomicity. The script runs as a single operation, preventing other commands from interleaving.
3.  **HTTP 429 vs 503?**
    *   429: User sent too many requests (Client fault).
    *   503: Server is overloaded/down (Server fault).
