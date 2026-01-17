# Day 48: Design Case - Web Crawler (Googlebot)

## 🎯 Goal
Design a scalable web crawler to download, parse, and index billions of web pages.
**Focus**: Scalability, Politeness, and Deduplication.

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start from seed URLs and discover new links.
2.  **Parse**: Extract text and metadata.
3.  **Store**: Save content for the Indexer.
4.  **Politeness**: Respect `robots.txt` and rate limits.

### Non-Functional
1.  **Scalability**: 1 Billion pages.
2.  **Extensibility**: Handle new content types (PDF, Images).
3.  **Robustness**: Handle traps (infinite loops), malformed HTML.

---

## 📐 Capacity Estimation
*   **Target**: 1 Billion pages/month.
*   **Throughput**: 1B / (30 * 24 * 3600) ≈ 400 pages/sec.
*   **Storage**: 1B * 100KB (avg size) = 100 TB.
*   **Storage Period**: 5 Years -> 6 PB.

---

## 🧠 Core Design Decisions

### 1. BFS vs DFS?
*   **DFS**: Too deep. Might get stuck in one domain (impolite).
*   **BFS**: Wide crawl. Better for discovering diverse content.
*   **Priority**: Actually, we use a **Priority Queue** based on PageRank/Freshness.

### 2. Duplicate Detection
*   **URL Level**: Canonicalize URL (`example.com` == `example.com/`). Bloom Filter.
*   **Content Level**:
    *   **Exact Match**: MD5/SHA256 Hash.
    *   **Near Duplicate**: **SimHash** (Hamming distance).

### 3. Politeness
*   Don't hammer one server.
*   Map `Hostname -> Queue`.
*   Each Queue has a delay (e.g., 2 seconds between requests).

---

## 🏗️ System Architecture

1.  **Seed URLs**: Starting point.
2.  **URL Frontier**: Manages the crawl queue.
    *   **Front Queue**: Prioritizer (High vs Low importance).
    *   **Back Queue**: Politeness (One queue per domain).
3.  **Fetcher**: Downloads the page (HTTP Client). Handles DNS (Cached).
4.  **Parser**: Validates HTML, extracts links.
5.  **Dedup**: Checks if content already exists (Bloom Filter/Redis).
6.  **Storage**: S3/HDFS for raw content.
7.  **Link Extractor**: Sends new URLs back to Frontier.

---

## 💻 Code Simulation: URL Frontier

A simplified simulation of a Priority-based URL Frontier.

```python
import queue
import hashlib
import time
import threading

class WebCrawler:
    def __init__(self):
        self.url_frontier = queue.PriorityQueue() # (priority, url)
        self.visited = set()
        self.lock = threading.Lock()

    def add_url(self, url, priority=1):
        with self.lock:
            if url not in self.visited:
                print(f"➕ Adding: {url} (Priority: {priority})")
                self.url_frontier.put((priority, url))
                self.visited.add(url)

    def crawl(self):
        while not self.url_frontier.empty():
            priority, url = self.url_frontier.get()
            print(f"🕷️ Crawling: {url} (Priority: {priority})")

            # Simulate processing
            content = f"Content of {url}"
            checksum = hashlib.md5(content.encode()).hexdigest()
            print(f"   💾 Saved: {checksum}")

            # Simulate finding new links
            if "google" in url:
                self.add_url("https://youtube.com", priority=2)

            time.sleep(0.5)

if __name__ == "__main__":
    crawler = WebCrawler()

    # Priority 1 = High, 5 = Low
    crawler.add_url("https://google.com", priority=1)
    crawler.add_url("https://example.com", priority=5)
    crawler.add_url("https://wikipedia.org", priority=2)

    crawler.crawl()
```

**Output:**
```
➕ Adding: https://google.com (Priority: 1)
➕ Adding: https://example.com (Priority: 5)
➕ Adding: https://wikipedia.org (Priority: 2)
🕷️ Crawling: https://google.com (Priority: 1)
   💾 Saved: dcbb3e761a381bfbb1db3596cca45497
➕ Adding: https://youtube.com (Priority: 2)
🕷️ Crawling: https://wikipedia.org (Priority: 2)
   💾 Saved: 0e3a4fe61124def226fc5c7bcdaa73a6
🕷️ Crawling: https://youtube.com (Priority: 2)
   💾 Saved: f2e935e7ac3b7b2dbb7cc6098568e7fc
🕷️ Crawling: https://example.com (Priority: 5)
   💾 Saved: 2fff569d176518f530603ff1552d61e0
```

---

## 🧠 Interview Nuances

### 1. How to handle Dynamic Pages (React/Angular)?
*   Simple fetchers only get empty HTML.
*   **Solution**: Use Headless Chrome (Puppeteer/Selenium) to render the page. Expensive/Slow.

### 2. What is a Spider Trap?
*   A loop: `example.com/a/b/c/a/b/c...`
*   **Solution**: Max URL length, Max path depth, or cycle detection.

### 3. DNS Resolution is a bottleneck?
*   DNS lookup can take 20ms - 500ms.
*   **Solution**: Build a custom DNS Cache (Map Hostname -> IP) to avoid repeated lookups.

---

## ⚡ Flashcards
1.  **What is SimHash?**
    *   A hashing algorithm where similar contents have similar hashes (small Hamming distance). Used for near-duplicate detection.
2.  **What is `robots.txt`?**
    *   A standard file websites use to communicate with crawlers, specifying which parts of the site should not be processed.
3.  **Why use Consistent Hashing in a Crawler?**
    *   To distribute URLs among different Downloader servers based on Hostname. Ensures one host is always handled by one server (easier for politeness).
