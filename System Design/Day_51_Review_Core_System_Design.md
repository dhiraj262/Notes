# Day 51: Review - Core System Design Cases

## 🎯 Goal
Consolidate knowledge from the Core System Design cases covered in Week 7.
**Focus**: Reviewing key architectures, trade-offs, and "Magic Numbers".

---

## 📊 Summary of Designs

| System | Key Challenge | Key Technology/Pattern |
| :--- | :--- | :--- |
| **Chat App (WhatsApp)** | Real-time delivery, Ordering | WebSockets, Cassandra (Write Heavy) |
| **Rate Limiter** | Distributed Counting, Race Conditions | Redis + Lua Scripts, Token Bucket |
| **Key-Value Store** | High Availability, Partitioning | Consistent Hashing, Vector Clocks, Gossip |
| **Web Crawler** | Politeness, Scale, Deduplication | URL Frontier, Bloom Filters, SimHash |
| **YouTube/Netflix** | Bandwidth, Storage, Latency | CDN, Adaptive Streaming (HLS/DASH), S3 |
| **Google Drive** | Sync, Bandwidth Efficiency | Chunking, Rolling Hash, Deduplication |

---

## 🧠 Key Patterns & Takeaways

### 1. Read vs Write Heavy
*   **Chat App**: Write Heavy (Incoming messages). Needs LSM Trees (Cassandra).
*   **YouTube**: Read Heavy (Streaming). Needs Caching (CDN).
*   **Web Crawler**: Write Heavy (Downloading pages). Needs fast I/O.

### 2. State Management
*   **Stateless**: Notification Service, Video Transcoder. Easy to scale (add more containers).
*   **Stateful**: WebSocket Gateway, Rate Limiter (Redis). Harder to scale (stickiness, sharding).

### 3. Data Consistency
*   **Strong**: Google Drive Metadata (File versions must be correct).
*   **Eventual**: YouTube View Counts, Chat "Read Receipts".

---

## ⚡ Quick Flashcard Review

### Q1: Why use WebSockets for Chat instead of HTTP?
> **Answer**: HTTP is request-response. Polling is inefficient. WebSockets provide a persistent, full-duplex connection allowing the server to push messages instantly.

### Q2: How does Consistent Hashing help in a KV Store?
> **Answer**: It minimizes data movement when adding/removing nodes. Only $K/N$ keys need to move, where $K$ is keys and $N$ is nodes.

### Q3: What is the purpose of a Bloom Filter in a Crawler?
> **Answer**: To quickly check if a URL has already been visited with low memory usage. It avoids infinite loops and re-crawling.

### Q4: Explain Adaptive Bitrate Streaming.
> **Answer**: The video is encoded in multiple qualities (360p, 1080p). The client player dynamically switches between them based on current network speed to prevent buffering.

### Q5: Why is Rolling Hash better than Fixed Hash for File Sync?
> **Answer**: Fixed hashing shifts all boundaries if data is inserted at the start, breaking all chunks. Rolling hash finds boundaries based on content patterns, so only the changed chunk is affected.

---

## 🛠️ Practice Exercise
pick one system from this week (e.g., **Chat App**) and:
1.  Draw the High-Level Architecture from memory.
2.  Write the schema for the main database tables.
3.  Calculate the storage requirement for 5 years.
