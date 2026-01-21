# Day 48: Design Case - Web Crawler

## 🎯 Goal
Design a scalable web crawler (like Googlebot) to download and index billions of web pages.
**Focus**: URL Frontier, Politeness, and Deduplication.

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start from seed URLs, follow links, download content.
2.  **Parse**: Extract text and new links.
3.  **Store**: Save content for the Indexer.

### Non-Functional
1.  **Scale**: Billions of pages.
2.  **Politeness**: Don't hammer a single domain. Respect `robots.txt`.
3.  **Robustness**: Handle traps (infinite loops), malformed HTML.
4.  **Freshness**: Re-crawl important pages frequently.

---

## 📐 Capacity Estimation
*   **Target**: 1 Billion pages per month.
*   **QPS**: 1B / 30 days / 86400 ≈ **400 pages/sec**.
*   **Storage**: 1B pages * 100KB (avg) = 100 TB/month.
    *   Need compressed storage (BigTable/HBase).

---

## 🧠 Core Design Decisions

### 1. Traversal: BFS vs DFS
*   **DFS**: Might get stuck in one domain (Spider Trap).
*   **BFS**: Better coverage. Crawl level 1, then level 2.
*   **Priority**: Not strict BFS. Prioritize "PageRank" or "Update Frequency".

### 2. URL Frontier (The Scheduler)
*   Manages the queue of URLs to crawl.
*   **Politeness**: Needs `QueueRouter` -> `DomainQueues`.
    *   One queue per domain (e.g., `cnn.com` queue).
    *   Worker fetches from `cnn.com` queue with a delay (e.g., 2s) between requests.

### 3. Deduplication
*   **URL Dedup**: Have we seen `example.com/a`?
    *   Use **Bloom Filter** (Memory efficient) or Redis Set.
*   **Content Dedup**: Is this page same as that one? (Mirrors).
    *   Use **SimHash** or **Rabin Fingerprint**. If Hamming Distance is small, pages are duplicates.

---

## 🏗️ System Architecture

1.  **Seed URLs**: Input list.
2.  **URL Frontier**: Prioritizes and enforces politeness. Gives URL to Fetcher.
3.  **HTML Fetcher**: Resolves DNS (Cached), downloads page.
4.  **Content Parser**: Validates HTML, checks `robots.txt`.
5.  **Content Dedup**: Calculates checksum. Checks DB. If new, save to **Content Store**.
6.  **Link Extractor**: Finds `<a href="...">`.
7.  **URL Filter/Dedup**: Discards ads, blacklisted sites, seen URLs.
8.  **Add to Frontier**: New links go back to step 2.

---

## 💻 Code Simulation: Simple Frontier

```python
import queue
import time
import threading
from urllib.parse import urlparse

class URLFrontier:
    def __init__(self):
        self.front_queues = queue.PriorityQueue() # Prioritized URLs
        self.back_queues = {} # Domain -> Queue
        self.lock = threading.Lock()
        self.seen_urls = set()

    def add_url(self, url, priority=1):
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)
        self.front_queues.put((priority, url))

    def get_url(self):
        # Simplified: Just getting from priority queue
        # Real system maps Priority -> Domain Queue -> Worker
        if not self.front_queues.empty():
            p, url = self.front_queues.get()
            return url
        return None

class CrawlerWorker:
    def __init__(self, frontier):
        self.frontier = frontier

    def run(self):
        while True:
            url = self.frontier.get_url()
            if not url:
                break

            domain = urlparse(url).netloc
            print(f"🕷️ Crawling {url} (Domain: {domain})")

            # Simulate Network
            time.sleep(0.5)

            # Simulate finding links
            if "start" in url:
                self.frontier.add_url(f"http://{domain}/page1", priority=2)
                self.frontier.add_url(f"http://{domain}/page2", priority=2)

if __name__ == "__main__":
    frontier = URLFrontier()
    frontier.add_url("http://cnn.com/start", priority=1)
    frontier.add_url("http://bbc.com/start", priority=1)

    worker = CrawlerWorker(frontier)
    # Simulate run
    for _ in range(5):
        worker.run()
```

---

## 🧠 Interview Nuances

### 1. How to handle DNS lookups?
*   DNS is slow (100ms).
*   Solution: Build a dedicated **DNS Cache Server**. Keep DNS records in memory.

### 2. Spider Traps?
*   `example.com/a/b/c/d/e...` (Infinite directory depth).
*   Limit max URL length. Limit max hops from seed.

### 3. Server-Side Rendering (SSR) / Single Page Apps (SPA)?
*   Simple fetcher only sees `<script>`.
*   Need a **Headless Browser** (Puppeteer/Selenium) to render JS. Expensive! Only do for high-value sites.

---

## ⚡ Flashcards
1.  **What is Robots.txt?**
    *   A standard file (`/robots.txt`) telling crawlers which parts of the site they are not allowed to access.
2.  **Bloom Filter False Positives?**
    *   It might say "URL Seen" when it wasn't. Result: We skip a valid page. Acceptable loss for massive memory savings.
3.  **What is Politeness?**
    *   Wait time between requests to the same domain to avoid DoS-ing the target server.
