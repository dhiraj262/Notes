# Day 46: Design Case - Distributed Rate Limiter

## 🎯 Goal
Design a Distributed Rate Limiter to prevent abuse and protect services from being overwhelmed.
**Scale**: 1 Million requests per second.

---

## 🗣️ Requirements

### Functional
1.  **Limiting**: Restrict users to X requests per Y seconds (e.g., 10 req/min).
2.  **Granularity**: Support limits by UserID, IP, or API Key.
3.  **Feedback**: Return HTTP 429 "Too Many Requests" when limited.

### Non-Functional
1.  **Low Latency**: The check must be super fast (< 20ms).
2.  **Distributed**: Works across multiple servers. Global consistency (mostly).
3.  **High Availability**: If the rate limiter goes down, default to "Allow" (fail-open) to avoid blocking legitimate users.

---

## 📐 Capacity Estimation
*   **Traffic**: 1M req/sec.
*   **Storage**:
    *   Need to store counters for active users.
    *   If 10M active users/day, and each entry is 100 bytes.
    *   10M * 100B = 1GB (Fits easily in memory/Redis).

---

## 🧠 Core Design Decisions

### 1. Where to run it?
*   **Client-side**: Unreliable (can be forged).
*   **Application Code**: Hard to scale (local counters don't sync).
*   **Middleware / API Gateway**: **Best spot**. Centralized check before hitting backend.

### 2. Algorithms
*   **Token Bucket**: Good for allowing bursts. Memory efficient.
*   **Leaky Bucket**: Smooths out traffic. Hard to handle bursts.
*   **Fixed Window Counter**: Simple, but suffers from "edge case" (double traffic at window boundary).
*   **Sliding Window Log**: Very accurate, but expensive (stores timestamp of every request).
*   **Sliding Window Counter**: Best balance. Divides window into small sub-grids.

### 3. Implementation: Redis + Lua
*   We need atomicity (Get + Increment + Check).
*   Redis **Lua Scripts** execute atomically on the server side.
*   Reduces network round trips from 3 to 1.

---

## 🏗️ System Architecture

1.  **Client** sends request to **Load Balancer**.
2.  **API Gateway** intercepts request.
3.  **Rate Limiter Middleware** calls **Redis Cluster**.
    *   Executes Lua script to check/update tokens.
4.  **Result**:
    *   If allowed: Forward to Service.
    *   If denied: Return HTTP 429.

---

## 💻 Code Simulation: Token Bucket (Lazy Refill)

Simulating the **Token Bucket** algorithm which allows for bursts of traffic but enforces an average rate.

```python
import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate # tokens per second
        self.tokens = capacity
        self.last_refill_timestamp = time.time()

    def allow_request(self):
        self.refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def refill(self):
        now = time.time()
        delta = now - self.last_refill_timestamp
        tokens_to_add = delta * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_timestamp = now

class RateLimiterService:
    def __init__(self):
        self.user_buckets = {} # mock Redis

    def access_resource(self, user_id):
        # Create bucket if not exists (Capacity 5, 1 token/sec)
        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = TokenBucket(capacity=5, refill_rate=1)

        bucket = self.user_buckets[user_id]
        if bucket.allow_request():
            print(f"✅ User {user_id}: Request Allowed (Tokens left: {int(bucket.tokens)})")
        else:
            print(f"⛔ User {user_id}: Rate Limited! (Tokens left: {int(bucket.tokens)})")

if __name__ == "__main__":
    service = RateLimiterService()
    uid = "user_123"

    print("--- Burst of 6 requests (Capacity is 5) ---")
    for i in range(6):
        service.access_resource(uid)

    print("\n--- Sleeping 2 seconds (Refill 2 tokens) ---")
    time.sleep(2)

    print("--- New Request ---")
    service.access_resource(uid)
```

**Output:**
```
--- Burst of 6 requests (Capacity is 5) ---
✅ User user_123: Request Allowed (Tokens left: 4)
✅ User user_123: Request Allowed (Tokens left: 3)
✅ User user_123: Request Allowed (Tokens left: 2)
✅ User user_123: Request Allowed (Tokens left: 1)
✅ User user_123: Request Allowed (Tokens left: 0)
⛔ User user_123: Rate Limited! (Tokens left: 0)

--- Sleeping 2 seconds (Refill 2 tokens) ---
--- New Request ---
✅ User user_123: Request Allowed (Tokens left: 1)
```

---

## 🧠 Interview Nuances

### 1. Why Redis over DB?
*   Speed. RAM vs Disk. We need ms level response.
*   Redis supports atomic counters (INCR) and Lua scripts.

### 2. How to handle Race Conditions?
*   Two servers read "Count = 9" at same time, both increment to 10. Actual count is 11.
*   **Solution**: Use Redis Lua script (runs single-threaded) or `INCR` command which is atomic.

### 3. Rate Limiting by IP vs User ID?
*   **IP**: Good for DDOS, but fails for users behind NAT (shared IP).
*   **User ID**: Precise, but requires Login.
*   **Hybrid**: Limit by IP for unauthenticated endpoints; by User ID for authenticated ones.

---

## ⚡ Flashcards
1.  **What is a "Fail-Open" strategy?**
    *   If the Rate Limiter service fails, allow all requests to pass so business logic isn't blocked.
2.  **Token Bucket vs Leaky Bucket?**
    *   Token Bucket allows bursts (up to capacity). Leaky Bucket processes at a constant rate (no bursts).
3.  **HTTP Code for Rate Limit?**
    *   429 Too Many Requests.
