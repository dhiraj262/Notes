# Day 51: Review - Core System Design Cases

## 📅 Week 7 Summary
This week we covered the **Big 5** system design questions that appear in 90% of senior interviews. Each introduced a unique architectural pattern.

| Day | Topic | Key Pattern | "Kill Shot" Feature |
| :--- | :--- | :--- | :--- |
| **45** | **Chat App (WhatsApp)** | **WebSockets** | Handling "Last Seen" efficiently with Redis (Heartbeats). |
| **46** | **Rate Limiter** | **Redis + Lua** | Distributed atomic counting; avoiding race conditions. |
| **47** | **Key-Value Store** | **Consistent Hashing** | Tunable Consistency (N, R, W) & Vector Clocks. |
| **48** | **Web Crawler** | **URL Frontier** | Politeness using separate queues per domain. |
| **49** | **Youtube/Netflix** | **Transcoding DAG** | Adaptive Bitrate Streaming (HLS) & CDN Edge Caching. |
| **50** | **Google Drive** | **Block Chunking** | Delta Sync & Block-level Deduplication. |

---

## 🧠 Comparative Analysis

### 1. Real-Time vs Async
*   **Real-Time**: Chat App (WebSockets), Rate Limiter (Latency < 20ms).
*   **Async/Batch**: Web Crawler (Billions of pages), Youtube Transcoding (Heavy compute), Google Drive (Sync).
*   *Insight*: Know when to block the user (Synchronous) and when to say "We'll process this" (Asynchronous).

### 2. Database Choices
*   **Cassandra/HBase**: Chat History (Write Heavy), Web Crawler (Billions of rows).
*   **Redis**: Rate Limiter (Counters), Chat (Presence), Job Queues.
*   **Relational (SQL)**: Google Drive (Metadata hierarchy integrity).
*   **Blob Store (S3)**: Youtube (Videos), Drive (File Blocks).

### 3. Handling "Hot" Data
*   **Sharding**: Consistent Hashing (KV Store) distributes load.
*   **Caching**: CDNs (Youtube) offload static reads.
*   **Aggregation**: Rate Limiting aggregates counts in memory/Redis before hitting DB.

---

## ⚡ Master Flashcards (Week 7)

1.  **What is the difference between HLS and DASH?**
    *   Both are Adaptive Bitrate Streaming protocols. HLS (Apple) uses `.m3u8` playlists and `.ts` chunks. DASH (Google) uses `.mpd` manifest and `.m4s` chunks. Conceptually identical.
2.  **How does Consistent Hashing minimize data movement?**
    *   When a node is added/removed, only keys belonging to that node's neighbors are re-mapped (k/N keys), rather than re-mapping all keys (k keys) in standard Modulo hashing.
3.  **Why use a DAG (Directed Acyclic Graph) for video processing?**
    *   It allows breaking a complex job (Transcode 4K video) into small, independent, parallelizable tasks (Split -> Audio, 480p, 720p -> Merge) for speed and fault tolerance.
4.  **What is the "Sloppy Quorum" in Dynamo-style systems?**
    *   If a preferred node is down, another node temporarily accepts the write (hinted handoff) to maintain High Availability, sacrificing Strong Consistency temporarily.
5.  **How to detect infinite loops in a Web Crawler?**
    *   Use a checksum/hash of the page content (not just URL) to detect duplicates. Limit maximum crawl depth.

---

## 🛠️ Practice Exercise
**Design a "Pastebin" (Text Sharing Service)**
*   *Hint*: It's a simplified **Google Drive** (Storage) + **URL Shortener** (Keys).
*   **Reqs**: Upload text, get a short URL. Expires after X days.
*   **Storage**: S3 for text blobs? Or just a DB? (Depends on size limit).
*   **Key Gen**: KGS (Key Generation Service) vs On-the-fly hashing.
