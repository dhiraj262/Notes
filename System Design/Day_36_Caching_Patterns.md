# Day 36: Caching Patterns & Strategies

## 🎯 Goal
Understand how to make systems fast by storing data closer to the computation.
**Focus**: Caching patterns, eviction policies, and the "Hardest Problem in CS" (Cache Invalidation).

---

## 🧩 Key Concepts

### 1. Where to Cache?
*   **Browser**: Local storage, HTTP Cache-Control headers.
*   **CDN**: Edge servers caching static assets (images, CSS).
*   **Load Balancer**: Caching SSL sessions.
*   **Application**: In-memory (Ehcache).
*   **Database Layer**: Redis/Memcached.

### 2. Caching Patterns

#### A. Cache-Aside (Lazy Loading) - **Most Common**
*   **Read**: App checks Cache.
    *   Hit -> Return data.
    *   Miss -> App reads DB -> App writes to Cache -> Return data.
*   **Write**: App updates DB -> App deletes/invalidates Cache key.
*   **Pros**: Only requests data actually needed. Resilient to cache failure.
*   **Cons**: First request is slow (Cache Miss). Stale data if write doesn't invalidate correctly.

#### B. Write-Through
*   **Logic**: App writes to Cache. Cache immediately writes to DB.
*   **Pros**: Data in cache is always fresh.
*   **Cons**: High write latency (2 writes). Cache pollution (storing data that might never be read).

#### C. Write-Back (Write-Behind)
*   **Logic**: App writes to Cache (ACK immediately). Cache asynchronously writes to DB.
*   **Pros**: Extremely fast writes. Low DB load.
*   **Cons**: **Data Loss Risk**. If Cache dies before syncing to DB, data is gone.

---

## 🧠 Eviction Policies
When the cache is full, who gets kicked out?

### 1. LRU (Least Recently Used)
*   **Logic**: Discard items that haven't been used for the longest time.
*   **Implementation**: Doubly Linked List + HashMap.
    *   *Access*: Move node to head (O(1)).
    *   *Evict*: Remove tail (O(1)).
*   **Use Case**: Social media, standard web apps.

### 2. LFU (Least Frequently Used)
*   **Logic**: Discard items with the lowest hit count.
*   **Use Case**: Analytics, Asset usage.

### 3. TTL (Time To Live)
*   **Logic**: Every key expires after X seconds.
*   **Use Case**: Auth tokens, OTPs.

---

## 💻 Code Simulation: LRU Cache

A classic interview question. Implementation using Python's `OrderedDict` (which is effectively a DLL + Map).

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Move accessed item to the end (Most Recently Used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update value and mark as recent
            self.cache.move_to_end(key)
        self.cache[key] = value

        # If full, remove the first item (Least Recently Used)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Usage
lru = LRUCache(2)
lru.put(1, 1)
lru.put(2, 2)
print(lru.get(1))       # Returns 1. Cache: {2:2, 1:1}
lru.put(3, 3)           # Evicts key 2. Cache: {1:1, 3:3}
print(lru.get(2))       # Returns -1 (not found)
lru.put(4, 4)           # Evicts key 1. Cache: {3:3, 4:4}
print(lru.get(1))       # Returns -1
print(lru.get(3))       # Returns 3
print(lru.get(4))       # Returns 4
```

---

## ⚡ Redis vs Memcached

| Feature | Memcached | Redis |
| :--- | :--- | :--- |
| **Data Types** | Strings only | Strings, Lists, Sets, Hashes, Sorted Sets |
| **Persistence** | None (In-memory only) | RDB (Snapshots), AOF (Logs) |
| **Replication** | No | Master-Slave Replication |
| **Threading** | Multi-threaded (Good for scaling up) | Single-threaded (No locks, very fast) |
| **Use Case** | Simple Key-Value cache | Complex caching, Queues, Pub/Sub, Leaderboards |

---

## ⚠️ The Trap: Cache Penetration & Stampede

1.  **Cache Penetration**:
    *   *Problem*: User queries a key that doesn't exist in DB (e.g., ID=-1). Cache misses, DB misses. Malicious users can hammer the DB.
    *   *Fix*: **Bloom Filter** (Check if key *might* exist before hitting DB) or cache "Empty" results (null) with short TTL.

2.  **Cache Stampede (Thundering Herd)**:
    *   *Problem*: A popular key (e.g., "Homepage_News") expires. 10,000 requests hit cache -> miss -> ALL hit DB simultaneously.
    *   *Fix*: **Mutex Lock** (Only 1 request rebuilds cache, others wait) or **Probabilistic Early Expiration** (Refresh before it actually expires).

---

## ⚡ Flashcards
1.  **What is the difference between Cache-Aside and Read-Through?**
    *   In Cache-Aside, the *Application* is responsible for fetching from DB and populating cache. In Read-Through, the *Cache Library/Provider* does it; the app just asks the cache.
2.  **Why use Redis Sorted Sets?**
    *   Perfect for Leaderboards (Rank users by score) or Priority Queues.
3.  **Does Caching violate Strong Consistency?**
    *   Yes, almost always. You trade consistency for latency. You must accept that cached data might be stale for the duration of the TTL or until invalidation.
