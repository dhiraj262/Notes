# Day 51: Review - Core System Design Cases

## 🎯 Goal
Review and consolidate the high-level architecture patterns learned from the core design cases covered this week.
**Focus**: Identifying common patterns and trade-offs.

---

## 📚 Case Study Summary

### 1. Chat App (WhatsApp)
*   **Key Pattern**: **WebSockets** for real-time delivery + **Push Notifications** for offline users.
*   **Storage**: **LSM Trees** (Cassandra) for write-heavy chat history.
*   **Challenge**: Maintaining message ordering and fan-out for large groups.

### 2. Rate Limiter
*   **Key Pattern**: **Middleware/Sidecar** interceptor.
*   **Algorithm**: **Token Bucket** (Bursty) vs **Leaky Bucket** (Smooth).
*   **Storage**: **Redis** with **Lua Scripts** to prevent race conditions during distributed counting.

### 3. Key-Value Store (DynamoDB)
*   **Key Pattern**: **Consistent Hashing** for partitioning.
*   **Consistency**: **Quorums** (W + R > N) for tunable consistency.
*   **Recovery**: **Merkle Trees** for anti-entropy (syncing data) and **Gossip Protocol** for membership.

### 4. Web Crawler (Googlebot)
*   **Key Pattern**: **URL Frontier** for scheduling and politeness.
*   **Deduplication**: **Bloom Filters** (URL seen?) and **SimHash** (Content similar?).
*   **Traps**: Detecting infinite loops and spider traps.

### 5. Video Streaming (YouTube)
*   **Key Pattern**: **CDN** for edge delivery.
*   **Processing**: **DAG** (Directed Acyclic Graph) for splitting transcoding jobs into parallel workers.
*   **Delivery**: **Adaptive Bitrate Streaming** (HLS/DASH) to adjust quality based on user bandwidth.

### 6. Cloud Storage (Google Drive)
*   **Key Pattern**: **Chunking** files for parallel upload and delta sync.
*   **Separation**: **Metadata** (SQL/ACID) is separate from **Block Data** (Immutable Blob Storage).
*   **Dedup**: Hashing chunks to avoid storing duplicates.

---

## 🧩 Common Patterns Identified

| Pattern | Use Case | Example |
| :--- | :--- | :--- |
| **Pub/Sub** | Decoupling producers/consumers | Chat, Notification System |
| **Partitioning** | Scaling Data | KV Store (Consistent Hashing), Chat (User ID) |
| **Caching** | Reducing Latency | Rate Limiter (Redis), Video (CDN) |
| **Async Processing** | Long-running tasks | Video Transcoding, Crawler Fetching |
| **Idempotency** | Retrying safely | Payment (Stripe), Messaging (Kafka) |

---

## 🛠️ Practical Task: "The Hybrid"

**Design a Live Video Commenting System (Twitch Chat)**
*   **Combine**:
    *   **Video Streaming** (Low latency, HLS).
    *   **Chat System** (High throughput, 1M users in one room).
*   **Challenge**: 1 Million users typing "LOL" at the same time.
    *   *Hint*: You cannot push 1M messages to 1M users (1 Trillion events). You need **Message Aggregation** or **Sampling** (Drop messages, only show 1%).

---

## ⚡ Flashcards
1.  **What is the difference between Transcoding and Encoding?**
    *   Encoding is compressing raw video. Transcoding is converting from one encoding/resolution to another.
2.  **When to use consistent hashing?**
    *   When you have a distributed cache or DB where nodes are added/removed frequently, and you want to minimize data movement.
3.  **Why is "Fan-out on Read" better for large groups?**
    *   Writing 1 message to 1M inboxes (Fan-out on Write) is too slow. Storing 1 message and having 1M users read it (Fan-out on Read) is easier on the DB.
