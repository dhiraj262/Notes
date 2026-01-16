# Day 51: Review - Core System Design Cases

## 🎯 Goal
Review and consolidate the high-frequency system design cases covered in Week 7. These are the "bread and butter" of senior engineering interviews.

## 📝 Summary of Topics

### Day 45: Chat App (WhatsApp)
*   **Core**: WebSockets for real-time.
*   **DB**: HBase/Cassandra for write-heavy history.
*   **Key Insight**: Separate "Online Status" service (Redis) from "Message" service.
*   **Trap**: Don't use polling. Don't use RDBMS for chat logs at scale.

### Day 46: Rate Limiter
*   **Core**: Protect services from abuse.
*   **Algo**: Token Bucket (Bursts allowed) vs Sliding Window (Smoother).
*   **Implementation**: Redis + Lua Scripts for atomic distributed counting.
*   **Key Insight**: Middleware pattern (API Gateway). Fail-open if limiter crashes.

### Day 47: Key-Value Store (Dynamo)
*   **Core**: High availability, leaderless replication.
*   **Algo**: Consistent Hashing (Ring) for partitioning.
*   **Consistency**: Tunable ($W+R > N$). Vector Clocks for conflict resolution.
*   **Storage**: LSM Trees (Write optimized).

### Day 48: Web Crawler
*   **Core**: Fetch, parse, store internet.
*   **Algo**: BFS with Priority (URL Frontier). Bloom Filters for visited set.
*   **Key Insight**: Politeness is crucial (delay queues). DNS is a bottleneck.

### Day 49: Video Streaming (Netflix)
*   **Core**: Deliver massive files with low latency.
*   **Algo**: Adaptive Bitrate Streaming (ABS). Client picks quality based on bandwidth.
*   **Storage**: Pre-signed URLs for upload. CDN for delivery.
*   **Key Insight**: Transcoding DAG to support multiple formats.

### Day 50: Cloud Storage (Google Drive)
*   **Core**: Sync files across devices.
*   **Algo**: Block-level chunking + Deduplication (Content Addressable).
*   **Key Insight**: Delta Sync saves bandwidth. ACID DB needed for metadata/hierarchy.

---

## 🏗️ Comparative Architecture Table

| System | Primary Protocol | Data Storage | Key Algorithm | Trade-off |
| :--- | :--- | :--- | :--- | :--- |
| **Chat** | WebSocket | Cassandra (Wide Column) | Sequence Gen / Fan-out | Latency vs Consistency |
| **Rate Limit**| HTTP/gRPC | Redis (In-memory) | Token Bucket / Lua | Accuracy vs Latency |
| **KV Store** | TCP (Internal) | LSM Tree (SSTable) | Consistent Hashing | Availability vs Consistency |
| **Crawler** | HTTP | Object Store + NoSQL | Bloom Filter / SimHash | Freshness vs Politeness |
| **Netflix** | HLS/DASH (HTTP) | S3 + CDN | Adaptive Bitrate | Quality vs Buffering |
| **GDrive** | HTTPS | S3 (Blocks) + SQL (Meta) | Dedup / Delta Sync | Storage Cost vs Complexity |

---

## 🧠 Common Interview Patterns (The "Meta")

1.  **The "Push vs Pull" Decision**:
    *   *Chat*: Push (WebSocket).
    *   *Feed*: Pull (Client requests).
    *   *Monitoring*: Push (Agents send metrics).

2.  **The "Data Store" Decision**:
    *   *Structured/Relational* -> SQL (Users, Orders, Billing).
    *   *Unstructured/Blob* -> S3 (Videos, Images, File Blocks).
    *   *High Write/Time Series* -> Cassandra/HBase (Chat logs, Sensor data).
    *   *Transient/Fast* -> Redis (Cache, Sessions, Rate Limits).

3.  **The "Idempotency" Check**:
    *   Always ask: "What happens if the network fails after I send the request but before I get the ACK?"
    *   Solution: Retry keys, Idempotency tokens.

## ⚡ Quick Fire Review (Self-Test)
1.  **Q**: Why not use SQL for WhatsApp messages?
    *   *A*: SQL B-Trees degrade with random writes at billion-scale. LSM Trees (Cassandra) handle append-only writes better.
2.  **Q**: How does Netflix optimize for slow networks?
    *   *A*: Adaptive Bitrate Streaming (switching to lower quality chunks on the fly).
3.  **Q**: How does Google Drive save space?
    *   *A*: Deduplication at the block level. If 100 people have the same viral video, it's stored once.
4.  **Q**: What is the "Thundering Herd" in caching?
    *   *A*: Many clients hitting DB simultaneously when a cache key expires. Solution: Request coalescing or random expiration.
