# Day 51: Review - Core System Design Cases

## 📝 Week 7 Summary
This week we covered the **Top 6** most common system design interview questions. These problems test your ability to apply the building blocks (Caching, Queues, Databases) to specific product requirements.

1.  **Chat App (WhatsApp)**: Real-time bi-directional communication using **WebSockets**. Key challenge: Storing message history efficiently (**Cassandra**).
2.  **Rate Limiter**: Distributed control using **Redis + Lua**. Key challenge: Race conditions and selecting the right algorithm (**Sliding Window Counter**).
3.  **Key-Value Store (Dynamo)**: Understanding distributed systems theory. Key challenge: **Partitioning (Consistent Hashing)**, **Replication**, and **Consistency (Quorums)**.
4.  **Web Crawler**: Large-scale data ingestion. Key challenge: **Politeness**, **Deduplication**, and managing the **URL Frontier**.
5.  **Video Streaming (YouTube)**: Large file delivery. Key challenge: **Transcoding** to multiple formats and **Adaptive Bitrate Streaming** via **CDN**.
6.  **Cloud Storage (Google Drive)**: File synchronization. Key challenge: **Chunking** large files for resumable uploads and **Deduplication** to save space.

---

## 🧩 Key Patterns Identified

| Pattern | Used In | Why? |
| :--- | :--- | :--- |
| **WebSockets** | Chat, Notifications | Low-latency, persistent connection for real-time updates. |
| **Consistent Hashing** | KV Store, Chat (Sticky Sessions) | Distributing data/load while minimizing movement when nodes change. |
| **Bloom Filters** | Web Crawler, KV Store | efficiently checking "Have I seen this before?" without disk seek. |
| **Chunking** | Video, Google Drive | Handling massive files by breaking them down. Parallel processing. |
| **Append-Only Logs** | Chat (Cassandra), KV Store | Optimizing for high write throughput. |
| **CDN (Edge)** | Video, Static Assets | Moving heavy content closer to users to reduce latency. |

---

## ⚡ Rapid Fire Flashcards

1.  **Q: Why use UDP for live video calls but TCP for Netflix?**
    *   A: Live calls need low latency; dropping a few frames is okay (UDP). Movies need 100% quality; buffering is acceptable to ensure completeness (TCP/HTTP).

2.  **Q: What is the "High Water Mark" in a Rate Limiter?**
    *   A: It's not a standard term, but usually refers to the queue length or load at which we start dropping requests aggressively.

3.  **Q: How does Consistent Hashing solve the "Hot Shard" problem?**
    *   A: It doesn't solve it completely! Virtual Nodes help smooth out the distribution, but a single popular key (e.g., Justin Bieber's tweets) can still overload a node.

4.  **Q: In a Web Crawler, why is DNS a bottleneck?**
    *   A: DNS lookups are synchronous and depend on external servers. A crawler making millions of requests needs a custom, cached, asynchronous DNS resolver.

5.  **Q: What is "Transcoding"?**
    *   A: Converting a video file from one format/bitrate to another (e.g., 1080p MP4 -> 360p HLS) to support different devices and network speeds.

6.  **Q: How does Google Drive save storage space when 100 people upload the same PDF?**
    *   A: **Block-level Deduplication**. It hashes the file chunks. If the hash exists, it references the existing chunk instead of storing a duplicate.

7.  **Q: What is a "Sloppy Quorum"?**
    *   A: In Dynamo-style systems, if a replica node is down, the write is temporarily stored on a healthy non-replica node (hinted handoff) to maintain availability, even if durability is temporarily reduced.

---

## ⚠️ Common Interview Pitfalls

1.  **Magic Numbers**: Don't just say "We need 100 servers." Calculate it: "10M req/day -> 115 req/sec. One server handles 1000 req/sec. We need ~2 servers + redundancy."
2.  **Ignoring "The Bad Path"**: Everyone designs for the happy user. What happens when the DB crashes? What happens when the user goes offline mid-sync? **Mention Failure Scenarios**.
3.  **Over-Engineering**: Don't use Kubernetes, Kafka, and GraphQL for a simple MVP unless the scale demands it. Start simple, then scale.
4.  **Forgetting Monitoring**: Always add a "Telemetry/Logging" service to your design. How else will you know if it's working?

---

## 🔜 Next Steps: Week 8
We move from "Core Apps" to **"Advanced Data Systems"**.
*   **Search Engines** (Elasticsearch internals).
*   **Distributed Logging** (ELK Stack).
*   **Stream Processing** (Kafka/Flink).
*   **Geo-Spatial Indexing** (Uber/Yelp).
