# Day 51: Review - Week 7 (System Design Cases)

## 🎯 Goal
Consolidate the architecture patterns learned from the major design cases this week.
**Focus**: Identifying the "Heart" of each system.

---

## 🧩 The "Heart" of Each System

### 1. Chat App (WhatsApp)
*   **Heart**: **WebSocket + Stateful Session Service**.
*   **Key DB**: Cassandra/HBase (Write-heavy log).
*   **Lesson**: Push models require persistent connections and careful state management.

### 2. Rate Limiter
*   **Heart**: **Redis + Lua Script**.
*   **Key Algo**: Token Bucket.
*   **Lesson**: Distributed locking is slow; atomic scripts are fast.

### 3. Key-Value Store (Dynamo)
*   **Heart**: **Consistent Hashing Ring**.
*   **Key Concept**: Tunable Consistency (R + W > N).
*   **Lesson**: Availability vs Consistency is a spectrum, not a binary choice.

### 4. Web Crawler
*   **Heart**: **URL Frontier**.
*   **Key Issue**: Politeness & Traps.
*   **Lesson**: The challenge isn't fetching, it's scheduling *what* and *when* to fetch.

### 5. Youtube/Netflix
*   **Heart**: **CDN + Adaptive Bitrate Streaming**.
*   **Key Flow**: Upload -> Transcode -> S3 -> CDN.
*   **Lesson**: Move bits close to the user (CDN) and adapt to their constraints (ABR).

### 6. Google Drive
*   **Heart**: **Block-Level Deduplication**.
*   **Key Split**: Metadata (SQL) vs Data (Object Storage).
*   **Lesson**: Never upload the same data twice.

---

## ⚡ Master Flashcards (Week 7)

1.  **Which database is best for Chat History?**
    *   Wide-Column Stores (Cassandra/HBase) because they handle high write throughput and time-series data efficiently.
2.  **How do you prevent a Crawler from DDoS-ing a site?**
    *   Politeness constraints in the URL Frontier (one queue per domain with delays).
3.  **What is the "Thundering Herd" in Caching?**
    *   When cache misses simultaneously for many users, causing a spike in load to the DB/Origin. Fix with Request Collapsing.
4.  **Why split Metadata and Data in Google Drive?**
    *   Metadata needs ACID (move folder), Data needs blob scalability (immutable chunks).
5.  **How does Consistent Hashing minimize data movement?**
    *   Only K/N keys move when a node is added/removed, where K is total keys and N is number of nodes.

---

## 🛠️ Practice
*   **Whiteboard**: Pick one random topic (e.g., Rate Limiter) and draw the architecture in 5 minutes.
*   **Code**: Re-write the `TokenBucket` class from memory.
