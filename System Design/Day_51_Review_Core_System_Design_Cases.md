# Day 51: Review - Core System Design Cases

## 📝 Summary
This week, we covered the most common and critical system design interview questions. These cases form the backbone of "Large Scale Distributed Systems" interviews.

---

## 🔍 Key Takeaways

### 1. Chat App (WhatsApp) - Day 45
*   **Core Protocol**: **WebSockets** for real-time bi-directional communication.
*   **Storage**: **Cassandra/HBase** for write-heavy chat history.
*   **Key Concept**: "Push" model for online users, "Pull/Store" for offline users.

### 2. Rate Limiter (Distributed) - Day 46
*   **Placement**: **API Gateway** or Middleware.
*   **Algorithms**: **Token Bucket** (Burst allowed) vs **Leaky Bucket** (Constant rate).
*   **Storage**: **Redis + Lua Scripts** for atomic counting.

### 3. Key-Value Store (Dynamo) - Day 47
*   **Partitioning**: **Consistent Hashing** (Ring with Virtual Nodes).
*   **Consistency**: Tunable (W + R > N).
*   **Failure**: Gossip Protocol, Hinted Handoff, Merkle Trees.

### 4. Web Crawler (Googlebot) - Day 48
*   **Architecture**: URL Frontier -> Fetcher -> Parser -> Storage.
*   **Politeness**: One queue per domain with delay.
*   **Deduplication**: Bloom Filters (URL) and SimHash (Content).

### 5. Video Streaming (Youtube) - Day 49
*   **Storage**: Object Storage (S3) for raw/processed video.
*   **Delivery**: **CDN** is critical.
*   **Streaming**: **Adaptive Bitrate Streaming (HLS/DASH)** to match user bandwidth.

### 6. File Storage (Google Drive) - Day 50
*   **Efficiency**: Block-level storage with **Deduplication** (Hash of blocks).
*   **Sync**: **Long Polling** to notify clients of changes.
*   **Metadata**: ACID compliant DB (SQL) separate from Block Storage (S3).

---

## 🧠 Pattern Recognition
*   **Read Heavy?** -> Cache (Redis) + CDN + Read Replicas.
*   **Write Heavy?** -> NoSQL (Cassandra) + Async Queues (Kafka).
*   **Real-time?** -> WebSockets.
*   **Global?** -> Geo-DNS + CDN + Multi-region replication.

---

## 🛠️ Action Items
1.  **Draw**: Pick one system (e.g., Chat App) and draw the architecture from memory on a whiteboard/paper.
2.  **Code**: Implement a simple **Token Bucket** class in Python without looking at the notes.
3.  **Read**: Skim through the "Design Data-Intensive Applications" chapter on *Partitioning*.

---

## ⏭️ Next Week
We dive into **Advanced Data Systems**: Search Engines (Elasticsearch), Distributed Logging, and Big Data Processing (Batch vs Stream).
