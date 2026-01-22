# Day 51: Review - Core System Design Cases

## 🎯 Goal
Consolidate the architectural patterns learned from the Core Design Cases (Week 7).

---

## 🧠 System Summaries

### 1. Chat App (WhatsApp)
*   **Key Tech**: WebSockets (Real-time), Cassandra (Write-heavy history).
*   **Pattern**: **Push Model** for active users, **Pull/Store** for offline users.
*   **Hardest Part**: Maintaining consistency of message ordering and managing millions of open connections.

### 2. Rate Limiter
*   **Key Tech**: Redis + Lua Scripts (Atomic operations).
*   **Algo**: Token Bucket (Allows bursts) vs Leaky Bucket (Smooths traffic).
*   **Placement**: API Gateway / Middleware.

### 3. Key-Value Store (Dynamo)
*   **Key Tech**: Consistent Hashing (Partitioning), Gossip Protocol (Failure Detection).
*   **Concept**: Tunable Consistency (W + R > N).
*   **Trade-off**: AP over CP (High Availability is king).

### 4. Web Crawler (GoogleBot)
*   **Key Tech**: URL Frontier (Priority Queue), Bloom Filters (Deduplication).
*   **Challenge**: **Politeness** (Don't DDOS sites) and handling **Spider Traps**.

### 5. Video Streaming (YouTube)
*   **Key Tech**: CDN (Edge Caching), Adaptive Bitrate Streaming (HLS/DASH).
*   **Pipeline**: Upload -> S3 -> Event -> Transcoding Workers -> S3 -> CDN.
*   **Concept**: Pre-compute everything (transcoding) to serve reads fast.

### 6. Cloud Storage (Google Drive)
*   **Key Tech**: Block-level Chunking (Deduplication), Differential Sync.
*   **Architecture**: Separation of Metadata (DB) and Block Data (Object Storage).
*   **Reliability**: Checksums and Replication are non-negotiable.

---

## 🧩 Common Patterns Identified

1.  **CQRS-lite**:
    *   Separating Read and Write paths (e.g., YouTube Transcoding pipeline vs Streaming via CDN).
2.  **The "Queue" Buffer**:
    *   Almost every write-heavy system (Chat, Uploads, Crawler) puts a Queue (Kafka) between the Ingestion and the Processor to handle spikes.
3.  **Hybrid Storage**:
    *   Using SQL for Metadata (ACID) and NoSQL/Blob for Payload (Scalability).
4.  **Partitioning**:
    *   Sharding by `User_ID`, `Chat_ID`, or `Video_ID` is essential for horizontal scaling.

---

## ⚡ Flashcards

1.  **Which system uses "Consistent Hashing"?**
    *   Distributed Key-Value Stores (Dynamo, Cassandra) and Caches (Memcached clients).
2.  **Why use a Bloom Filter in a Crawler?**
    *   To efficiently check if a URL has already been visited without storing the full URL string in memory.
3.  **What is the "Thundering Herd" problem?**
    *   When a large number of processes wake up or retry at the same time, causing a resource spike. Solved with **Jitter**.
4.  **What is Backpressure?**
    *   When a consumer tells a producer to slow down (e.g., if the Transcoding workers are full, stop accepting new uploads or slow down the queue consumption).

---

## 🛠️ Weekly Challenge
Design a **Pastebin** (like Pastebin.com).
*   **Requirements**: Text upload, Expiry, Custom URLs.
*   **Hint**: It's a simplified URL Shortener + Object Store.
*   **Key Decision**: SQL vs NoSQL? (NoSQL Key-Value is great here).
