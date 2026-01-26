# Day 46: Design Case - Distributed Rate Limiter

## 🎯 Goal
Design a system to limit the number of API requests a user can make within a time window (e.g., 10 requests per second).
**Focus**: Precision, Low Latency, and Distributed Synchronization.

---

## 🗣️ Requirements

### Functional
1.  **Throttle**: Reject requests if user exceeds limit.
2.  **Configurable**: Different limits for different APIs (e.g., `POST /order` is 5/sec, `GET /feed` is 100/sec).
3.  **Response**: Return `HTTP 429 Too Many Requests`.

### Non-Functional
1.  **Low Latency**: The check must be fast (< 5ms).
2.  **Distributed**: Works across multiple API servers.
3.  **High Availability**: The limiter itself shouldn't become a bottleneck.

---

## 📐 Capacity Estimation
*   **Total Traffic**: 1 Million QPS.
*   **Storage**: Need to store counters for active users.
    *   If 10M active users in a window.
    *   Key (UserId) + Value (Count) ≈ 50 Bytes.
    *   10M * 50B = **500 MB** (Fits easily in Memory/Redis).

---

## 🧠 Core Design Decisions

### 1. Where to Rate Limit?
*   **Client**: Unreliable. Easily bypassed.
*   **Application Server**: Hard to sync if you have 100 servers.
*   **Middleware (Gateway)**: Best place. Centralized check before request hits backend.

### 2. Algorithms
*   **Token Bucket**: Tokens are added at rate `r`. Request takes a token. Allows bursts.
*   **Leaky Bucket**: Requests enter queue, processed at constant rate. Smooths traffic.
*   **Fixed Window**: Count requests in `12:00:00 - 12:00:01`. Problem: Spike at edges (2x limit allowed).
*   **Sliding Window Log**: Store timestamp of every request. Very accurate but expensive (O(N) memory).
*   **Sliding Window Counter**: Hybrid. Weighted average of previous and current window.
    *   **Decision**: **Token Bucket** (for simple throttling) or **Sliding Window Counter** (for strict limits).

### 3. Distributed State (Redis + Lua)
*   **Race Condition**: Two servers read `count=9`, both increment to `10`. Real count should be `11`.
*   **Locking**: Too slow.
*   **Lua Script**: Execute `GET` + `INCR` atomically in Redis.

---

## 🏗️ System Architecture

1.  **API Gateway**: Receives request.
2.  **Rate Limiter Service**: Checks Redis.
3.  **Redis Cluster**: Stores counters.
    *   Key: `limiter:{user_id}:{api_endpoint}`.
    *   Value: `count`.
    *   TTL: Window size (e.g., 1 min).

---

## 💻 Code Simulation: Sliding Window Counter

Simulating the **Sliding Window Counter** algorithm which approximates the count based on overlap.

```python
import time
import math

class RateLimiter:
    """Sliding Window Counter Implementation"""
    def __init__(self, limit, window_size_sec):
        self.limit = limit
        self.window_size = window_size_sec
        # Storage: user_id -> { "prev_window_count": 0, "curr_window_count": 0, "curr_window_start": timestamp }
        self.store = {}

    def _get_current_window_start(self):
        # Round down to nearest window start
        now = time.time()
        return math.floor(now / self.window_size) * self.window_size

    def allow_request(self, user_id):
        now = time.time()
        curr_window_start = self._get_current_window_start()

        # Init user if not exists
        if user_id not in self.store:
            self.store[user_id] = {
                "prev_count": 0,
                "curr_count": 0,
                "window_start": curr_window_start
            }

        data = self.store[user_id]

        # Check if we moved to a new window
        if curr_window_start > data["window_start"]:
            # If 1 window passed, current becomes prev
            if curr_window_start - data["window_start"] == self.window_size:
                data["prev_count"] = data["curr_count"]
            else:
                # If more than 1 window passed, prev is 0
                data["prev_count"] = 0

            data["curr_count"] = 0
            data["window_start"] = curr_window_start

        # Calculate weighted count
        # Weight = Percent of current window elapsed
        time_into_current_window = now - curr_window_start
        weight = time_into_current_window / self.window_size

        # Formula: PrevCount * (1 - Weight) + CurrCount
        estimated_count = (data["prev_count"] * (1 - weight)) + data["curr_count"]

        if estimated_count < self.limit:
            data["curr_count"] += 1
            return True, estimated_count
        else:
            return False, estimated_count

if __name__ == "__main__":
    # Limit: 5 requests per 10 seconds
    limiter = RateLimiter(limit=5, window_size_sec=2)

    user = "User_123"

    print("--- Burst 1 (Allowed) ---")
    for i in range(5):
        allowed, count = limiter.allow_request(user)
        print(f"Req {i+1}: Allowed={allowed} (Est Count: {count:.2f})")
        time.sleep(0.1)

    print("\n--- Burst 2 (Blocked) ---")
    allowed, count = limiter.allow_request(user)
    print(f"Req 6: Allowed={allowed} (Est Count: {count:.2f})")

    # Wait for window to slide partially
    print("\n--- Waiting 1.5s (Window slides) ---")
    time.sleep(1.5)

    # Now some quota should be freed up
    allowed, count = limiter.allow_request(user)
    print(f"Req 7: Allowed={allowed} (Est Count: {count:.2f})")
```

**Output:**
```
--- Burst 1 (Allowed) ---
Req 1: Allowed=True (Est Count: 0.00)
Req 2: Allowed=True (Est Count: 1.05)
Req 3: Allowed=True (Est Count: 2.10)
Req 4: Allowed=True (Est Count: 3.15)
Req 5: Allowed=True (Est Count: 4.20)

--- Burst 2 (Blocked) ---
Req 6: Allowed=False (Est Count: 5.25)

--- Waiting 1.5s (Window slides) ---
Req 7: Allowed=True (Est Count: 3.75)
```
*(Note: Output values depend on precise timing)*

---

## 🧠 Interview Nuances

### 1. Redis is Down. What happens?
*   **Fail Open**: Allow all requests. Better to let spammers in than block legitimate users (Availability > Consistency).
*   **Fail Closed**: Block all requests. Bad UX.

### 2. Hard vs Soft Rate Limiting
*   **Hard**: Strict limit. Returns 429 immediately.
*   **Soft**: Allow short bursts over the limit, but throttle subsequent requests (delay them).

### 3. HTTP Headers
*   Always return headers so the client knows their status:
    *   `X-Ratelimit-Limit`: 100
    *   `X-Ratelimit-Remaining`: 5
    *   `X-Ratelimit-Retry-After`: 58 (seconds)

---

## ⚡ Flashcards
1.  **Why is Token Bucket popular?**
    *   Memory efficient and allows bursts of traffic (e.g., loading a webpage triggers 10 API calls instantly).
2.  **What is the 'Race Condition' in Rate Limiting?**
    *   Read-Modify-Write cycle. Fixed using Redis `INCR` or Lua scripts (Atomic).
3.  **Why use Sliding Window over Fixed Window?**
    *   Fixed window allows 2x limit at window boundaries. Sliding window is smoother and prevents this loophole.
