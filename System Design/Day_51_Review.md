# Day 51: Review - Core System Design Cases

## 🎯 Goal
Review and consolidate knowledge from the "Core System Design Cases" week (Days 45-50).
This week covered: **Chat, Rate Limiter, KV Store, Web Crawler, Youtube/Netflix, Google Drive**.

---

## 🧠 Key Takeaways Summary

### 1. Chat App (WhatsApp)
*   **Key Tech**: WebSockets (Real-time), HBase/Cassandra (Write heavy history).
*   **Core Concept**: Decoupling "Online Delivery" from "Offline Storage".
*   **Trap**: Don't use polling. Don't use SQL for message history if scale is huge.

### 2. Rate Limiter (Distributed)
*   **Key Tech**: Redis + Lua Script (Atomic).
*   **Core Concept**: Token Bucket (Bursts allowed) vs Leaky Bucket (Constant rate).
*   **Trap**: Race conditions (Read-Modify-Write). Use `EVAL` in Redis.

### 3. Key-Value Store (Dynamo)
*   **Key Tech**: Consistent Hashing (Partitioning), Gossip Protocol (Failure Detection).
*   **Core Concept**: Tunable Consistency (`W + R > N`).
*   **Trap**: Thinking Strong Consistency is free. It costs latency/availability.

### 4. Web Crawler
*   **Key Tech**: URL Frontier (Priority Queues), DNS Cache, SimHash.
*   **Core Concept**: Politeness is crucial (don't DDoS sites).
*   **Trap**: Spider traps (infinite loops) and rendering JS (Headless Chrome).

### 5. Youtube/Netflix
*   **Key Tech**: CDN (Edge caching), Adaptive Bitrate (MPEG-DASH).
*   **Core Concept**: Transcoding Pipeline (DAG) to convert raw -> multi-format.
*   **Trap**: Trying to serve video from the DB. Always use Blob Store + CDN.

### 6. Google Drive
*   **Key Tech**: Chunking (Splitting files), Deduplication (Hashing).
*   **Core Concept**: Differential Sync (Only upload changed blocks).
*   **Trap**: Storing duplicate blocks wastes massive space.

---

## ⚡ Consolidated Flashcards

1.  **Which protocol is best for Chat Apps?**
    *   WebSockets (Persistent, Bi-directional).
2.  **What is the "Thundering Herd" in Rate Limiting?**
    *   Many requests hitting at the exact second a window resets. Fix with jitter.
3.  **What problem does Consistent Hashing solve?**
    *   Minimizes data movement when adding/removing nodes in a distributed cache/DB.
4.  **How do you handle conflict in Dynamo-style systems?**
    *   Vector Clocks or Last-Write-Wins (LWW).
5.  **Why split files into chunks for Google Drive?**
    *   To enable deduplication (save space) and delta sync (save bandwidth).
6.  **What is a Manifest File in streaming?**
    *   The playlist (`.m3u8`) telling the player which chunks to download.
7.  **What is Politeness in crawling?**
    *   Deliberately adding delays between requests to the same domain.

---

## 🛠️ Practice Exercise
Pick one system (e.g., Rate Limiter) and implement a working prototype using **Redis** and **Python** (using `redis-py`).
*   Try implementing the **Sliding Window Log** algorithm.
*   Measure how much memory it consumes compared to Fixed Window.

---

## 📅 Next Week Preview: Advanced Data Systems
*   **Search Engines (Elasticsearch)**
*   **Typeahead (Autocomplete)**
*   **Distributed Logging (ELK)**
*   **Big Data Processing (MapReduce/Spark)**
