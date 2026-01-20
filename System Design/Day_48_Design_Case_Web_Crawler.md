# Day 48: Design Case - Web Crawler

## 🎯 Goal
Design a scalable web crawler (like Googlebot) to index the entire web (billions of pages).
**Focus**: Politeness, URL Frontier (Scheduling), and Content Deduplication.

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start with seeds, fetch pages, extract links, repeat.
2.  **Robots.txt**: Respect `User-Agent` rules.
3.  **Storage**: Store HTML content for indexing.

### Non-Functional
1.  **Scale**: 1 Billion pages/month.
2.  **Politeness**: Don't hammer a single server (Wait between requests).
3.  **Extensibility**: Handle new content types (PDF, Images).

---

## 🧠 Core Design Decisions

### 1. BFS vs DFS?
*   **DFS**: Traps the crawler in one deep site (e.g., wikipedia recursion).
*   **BFS (Breadth-First Search)**: Better. Explores wide range of sites.
    *   **Decision**: BFS using a FIFO Queue.

### 2. URL Frontier (The Scheduler)
*   It's not just a simple Queue.
*   **Problem**: If queue has 1000 links from `cnn.com` in a row, we will DDoS CNN.
*   **Solution**:
    *   **Front Queues (Prioritizer)**: Sort by importance (PageRank).
    *   **Back Queues (Politeness)**: Map `Hostname -> Queue`. One queue per domain.
    *   **Heap**: Selects which queue to pop from next (Round Robin).

### 3. Duplication (SimHash)
*   30% of web pages are duplicates.
*   Storing exact string matches is expensive.
*   **SimHash**: Fingerprinting algorithm where similar docs have similar hashes (Hamming distance).

---

## 🏗️ System Architecture

1.  **Seed URLs**: Enters the system.
2.  **URL Frontier**: Prioritizes and buffers URLs.
3.  **HTML Downloader**:
    *   Fetches content.
    *   Uses **DNS Resolver** (Cached).
4.  **Content Parser**: Validates HTML, extracts links.
5.  **Dup Check**: Checks Redis/Bloom Filter ("Have we seen this URL?").
    *   Also checks Content Checksum ("Is this content same as another URL?").
6.  **Storage**: Save to S3/HBase.
7.  **Loop**: New links go back to URL Frontier.

---

## 💻 Code Simulation: Simple BFS Crawler

A local simulation of the fetch-parse-queue loop.

```python
from collections import deque
import time

class SimpleCrawler:
    def __init__(self):
        self.visited = set()
        self.queue = deque() # URL Frontier
        self.robots_disallowed = {"google.com/private"}

    def add_seed(self, url):
        self.queue.append(url)

    def is_allowed(self, url):
        # Mock Robots.txt check
        if url in self.robots_disallowed:
            return False
        return True

    def crawl(self):
        while self.queue:
            url = self.queue.popleft()

            if url in self.visited:
                continue

            if not self.is_allowed(url):
                print(f"⛔ Skipped (Robots.txt): {url}")
                continue

            # Mock Fetching
            print(f"🕸️ Fetching: {url}")
            # Simulate network delay + politeness
            time.sleep(0.1)
            self.visited.add(url)

            # Mock Parsing (Finding new links)
            new_links = self.parse_links(url)
            for link in new_links:
                if link not in self.visited:
                    self.queue.append(link)

    def parse_links(self, url):
        # Mock logic: return related pages
        if url == "google.com":
            return ["google.com/images", "google.com/private"]
        elif url == "google.com/images":
            return ["google.com/cats"]
        return []

if __name__ == "__main__":
    bot = SimpleCrawler()
    bot.add_seed("google.com")
    bot.crawl()
```

**Output:**
```
🕸️ Fetching: google.com
🕸️ Fetching: google.com/images
⛔ Skipped (Robots.txt): google.com/private
🕸️ Fetching: google.com/cats
```

---

## 🧠 Interview Nuances

### 1. Handling Dynamic Content (JS/React)
*   Standard HTTP requests only get the initial HTML (often empty).
*   **Solution**: Headless Browser (Puppeteer/Selenium) to render the page. Expensive (CPU heavy).

### 2. DNS Bottleneck
*   DNS lookup takes 10-200ms.
*   Crawler makes millions of requests.
*   **Solution**: Build a custom high-performance DNS cacher. Do not use standard OS DNS calls (synchronous).

### 3. Trap Detection
*   "Spider Traps": Infinite calendar links (`next_day?date=...`).
*   **Fix**: Limit URL length. Limit max depth per domain.

---

## ⚡ Flashcards
1.  **What is a URL Frontier?**
    *   The data structure that manages the queue of URLs to be downloaded, handling priority and politeness.
2.  **Bloom Filter use case in Crawling?**
    *   Efficiently checking if a URL has already been visited (Space efficient, low false positives).
3.  **What is Politeness?**
    *   The delay enforced between two requests to the same domain to avoid overloading it.
