# Day 46: Design a Rate Limiter (Distributed)

## 🎯 Goal
Design a system to throttle API requests to prevent abuse and protect backend services.
**Focus**: Algorithms, Distributed Counter Accuracy, and Latency.

---

## 🗣️ Requirements

### Functional
1.  **Throttle Rules**: Support rules like "10 requests per second (RPS)" or "500 requests per hour".
2.  **Granularity**: Limit by User ID, IP Address, or API Key.
3.  **Feedback**: Return HTTP 429 "Too Many Requests" when blocked.

### Non-Functional
1.  **Low Latency**: The check must be < 5ms.
2.  **Accuracy**: Should be reasonably accurate across distributed nodes.
3.  **Scalability**: Handle 100M concurrent requests.

---

## 📐 Capacity Estimation
*   **Total Requests**: 1 Billion/day -> 12,000 RPS avg -> 100k RPS peak.
*   **Storage**: Need to store counters.
    *   100M active users * 1KB counter data = 100GB RAM.
    *   *Decision*: Use **Redis** (In-memory is fast).

---

## 🧠 Core Design Decisions

### 1. Where to place the Rate Limiter?
*   **Client Side**: Unreliable (can be forged).
*   **Server Side (Inside API)**: Hard to scale if API is stateless.
*   **Middleware / API Gateway**: Best place. Centralized control before hitting backend.

### 2. Algorithms
*   **Token Bucket**: Good for allowing bursts. (Standard choice).
*   **Leaky Bucket**: Smooths out bursts. Good for queues.
*   **Fixed Window**: Simple, but suffers from "edge case spikes" (2x traffic at minute boundary).
*   **Sliding Window Log**: Very accurate, but expensive (stores every timestamp).
*   **Sliding Window Counter**: Best balance of accuracy and memory.

### 3. Distributed State
*   If we have 10 API Gateway nodes, they need a shared counter.
*   **Redis** is the standard solution.
*   *Race Condition*: Two nodes read "Count=9" at the same time and both increment to 10.
    *   *Fix*: **Lua Scripts** in Redis (Atomic execution).

---

## 🏗️ System Architecture

1.  **Client**: Sends Request.
2.  **Load Balancer**: Routes to API Gateway.
3.  **API Gateway (Rate Limiter Middleware)**:
    *   Extracts User ID / IP.
    *   Calls **Redis** to check/increment counter.
    *   If allowed -> Forward to **Service**.
    *   If denied -> Return **HTTP 429**.

### Redis Data Structure (Sliding Window Counter)
*   Key: `limiter:{user_id}:{timestamp_minute}`
*   Value: `count`
*   Also read `limiter:{user_id}:{previous_minute}` to interpolate.

---

## 💻 Code Simulation: Token Bucket Algorithm

A Python implementation of the classic Token Bucket algorithm (in-memory).

```python
import time

class RateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity        # Max tokens (burst size)
        self.tokens = capacity          # Current tokens
        self.refill_rate = refill_rate  # Tokens per second
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        delta = now - self.last_refill

        # Calculate tokens to add
        tokens_to_add = delta * self.refill_rate

        # Refill, but don't exceed capacity
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def allow_request(self, tokens_needed=1):
        self._refill()
        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False

if __name__ == "__main__":
    # Capacity 5, Refill 1 token/sec
    limiter = RateLimiter(capacity=5, refill_rate=1)

    print("🚀 Sending 5 bursts...")
    for i in range(5):
        if limiter.allow_request():
            print(f"   ✅ Request {i+1}: Allowed")
        else:
            print(f"   ⛔ Request {i+1}: Denied")

    print("🚀 Sending 6th burst (Should Fail)...")
    if limiter.allow_request():
        print("   ✅ Request 6: Allowed")
    else:
        print("   ⛔ Request 6: Denied (Correct)")

    print("💤 Sleeping 2 seconds...")
    time.sleep(2)

    print("🚀 Sending after sleep (Should Allow)...")
    if limiter.allow_request():
        print("   ✅ Request 7: Allowed (Refilled)")
    else:
        print("   ⛔ Request 7: Denied")
```

---

## 🧠 Interview Nuances

### 1. How to handle Distributed Race Conditions?
*   **Naive**: Read(Redis) -> If < Limit -> Incr(Redis). **Fail**: Not atomic.
*   **Better**: `INCR` command returns the new value. If new value > limit, reject.
*   **Best**: Redis **Lua Script**. Bundles the "Check and Increment" into one atomic operation.

### 2. What if Redis goes down?
*   **Fail Open**: Allow all requests. Better to risk overload than to block all users (Availability > Consistency).
*   **Fail Closed**: Block all requests. Safe, but bad UX.

### 3. Client Header Standards?
*   Return headers so client knows their status:
    *   `X-Ratelimit-Limit`: 100
    *   `X-Ratelimit-Remaining`: 55
    *   `X-Ratelimit-Retry-After`: 10s

---

## ⚡ Flashcards
1.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows *bursts*. Leaky Bucket forces a *constant output rate*.
2.  **Why use Redis for Rate Limiting?**
    *   extremely fast (in-memory), supports atomic operations (INCR, Lua), and Time-To-Live (TTL) for auto-expiry.
3.  **What is a "Thundering Herd" in this context?**
    *   If many blocked clients retry exactly at the same time when the window resets. Fix: Add Jitter (random noise) to `Retry-After`.
