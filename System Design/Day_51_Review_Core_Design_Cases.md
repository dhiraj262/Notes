# Day 51: Review - Core System Design Cases

## 🎯 Goal
Review and consolidate knowledge from the core design cases covered in Week 7. Focus on identifying common patterns and trade-offs.

---

## 🔁 Summary of Week 7

### Day 45: Chat App (WhatsApp)
*   **Key Tech**: WebSockets (Real-time), Cassandra (Write-heavy history), Redis (User Session/Presence).
*   **Takeaway**: Push vs Pull models. Handling 1-on-1 vs Group Chat fan-out.

### Day 46: Rate Limiter
*   **Key Tech**: Redis (Counters), Lua Scripts (Atomicity).
*   **Algorithms**: Token Bucket (Bursts allowed), Sliding Window (Accurate).
*   **Takeaway**: Middleware placement (API Gateway) is crucial for protection.

### Day 47: Key-Value Store (Dynamo)
*   **Key Tech**: Consistent Hashing (Partitioning), Gossip Protocol (Failure Detection), Merkle Trees (Sync).
*   **Takeaway**: Tunable Consistency (W+R > N) vs Availability.

### Day 48: Web Crawler
*   **Key Tech**: URL Frontier (Politeness), DNS Cache, Bloom Filters (Dedup).
*   **Takeaway**: The importance of being a "good citizen" (Politeness) while crawling at scale.

### Day 49: Youtube/Netflix
*   **Key Tech**: CDN (Edge Delivery), Adaptive Bitrate (DASH/HLS), Transcoding (DAG).
*   **Takeaway**: Bandwidth is the bottleneck. Move data closer to users.

### Day 50: Google Drive
*   **Key Tech**: Block-Level Deduplication, Differential Sync, Metadata vs Blob separation.
*   **Takeaway**: Optimization of upload bandwidth is the competitive advantage.

---

## 🧩 Common Patterns Identified

1.  **The "Coordinator" Pattern**
    *   Seen in: KV Store, Rate Limiter.
    *   A node that routes requests to the correct worker/shard.

2.  **The "Separation of Concerns" Pattern**
    *   Seen in: Google Drive (Metadata vs Blocks), Youtube (Manifest vs Chunks).
    *   Split the "Control Plane" (Small, Complex, ACID) from the "Data Plane" (Huge, Simple, Immutable).

3.  **The "Async Processing" Pattern**
    *   Seen in: Youtube (Transcoding), Chat (Push Notifications).
    *   Don't block the user. Put heavy jobs in a Queue.

---

## ⚡ Review Flashcards

1.  **Why did we use Cassandra for Chat but S3 for Youtube?**
    *   Chat = Billions of small text writes (Cassandra excels at small, fast writes).
    *   Youtube = Large immutable blobs (S3 excels at storage density and throughput).
2.  **How does Consistent Hashing minimize data movement?**
    *   When a node is added/removed, only neighbors are affected. In modulo hashing (`% N`), *every* key might move.
3.  **What is the "Thundering Herd" problem?**
    *   When many processes wake up at once to handle an event (e.g., Cache Expiry), overwhelming the system.
4.  **Difference between Strong and Eventual Consistency?**
    *   **Strong**: Read always returns latest Write. (High Latency/Lower Availability).
    *   **Eventual**: Read might return stale data, but system catches up. (Low Latency/High Availability).
5.  **What is a Bloom Filter's weakness?**
    *   False Positives (It might say "Exists" when it doesn't). It never has False Negatives.

---

## 🛠️ Action Item
*   Pick **ONE** design case from this week.
*   Try to implement a **mini-version** of it in code (more detailed than the snippets provided).
*   For example, write a real **Rate Limiter** using a local Redis instance and Flask.
