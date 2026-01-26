# Day 48: Design a Web Crawler

## 🎯 Goal
Design a scalable web crawler to download and index billions of web pages (like GoogleBot).
**Focus**: URL Frontier (Management), Politeness, and Deduplication (Checksums).

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start from seed URLs and traverse links.
2.  **Storage**: Save HTML content and metadata.
3.  **Politeness**: Do not overload any single server (respect `robots.txt`).

### Non-Functional
1.  **Scalability**: Fetch 1 Billion pages/month.
2.  **Extensibility**: Support new protocols or content types.
3.  **Robustness**: Handle malformed HTML, 404s, and infinite loops.

---

## 📐 Capacity Estimation
*   **Target**: 1 Billion pages/month -> ~400 req/sec.
*   **Storage**: Avg page 100KB. 1B * 100KB = 100 TB/month.
*   **Time**: To crawl the whole web (wait times included), we need massively parallel workers.

---

## 🧠 Core Design Decisions

### 1. BFS vs DFS?
*   **DFS**: Might get stuck in deep recursive paths (Spider traps).
*   **BFS**: Better for covering wide ground. We want to crawl high-quality pages (Level 0, 1) first.
*   **Decision**: **BFS** (Breadth-First Search).

### 2. Handling Duplicates
*   30% of web content is duplicate.
*   **Solution**: Compute a 64-bit checksum (Fingerprint) of the content.
*   Store fingerprints in a set/Bloom Filter to check existence before saving.

### 3. URL Frontier (The Manager)
*   Need to prioritize URLs and handle politeness.
*   **Two Queues**:
    *   **Front Queues (Prioritizer)**: Based on PageRank or update frequency.
    *   **Back Queues (Politeness)**: Map to specific domains.
        *   Worker 1 is assigned "wikipedia.org". It pulls from Wikipedia queue, waits `X` seconds between fetches.

---

## 🏗️ System Architecture

1.  **Seed URLs**: Starting point.
2.  **URL Frontier**: Manages the queue of URLs to crawl.
3.  **DNS Resolver**: Caches IP addresses to speed up fetching.
4.  **HTML Downloader**: Fetches the page.
5.  **Content Parser**: Validates and extracts links.
6.  **Duplicate Eliminator**: Checks Checksum.
7.  **URL Filter**: Removes blacklisted URLs.
8.  **Storage**: Save to Blob Store (S3).

---

## 💻 Code Simulation: Simple Crawler

Simulating a basic BFS crawler with a visited set.

```python
import collections
import time

class WebCrawler:
    def __init__(self):
        self.visited = set()
        self.queue = collections.deque()
        self.mock_internet = {
            "google.com": ["gmail.com", "maps.google.com"],
            "gmail.com": ["google.com"],
            "maps.google.com": [],
            "facebook.com": ["instagram.com"],
            "instagram.com": ["facebook.com"]
        }

    def start_crawling(self, seed_url):
        self.queue.append(seed_url)
        self.visited.add(seed_url)

        while self.queue:
            url = self.queue.popleft()
            print(f"🕷️ Crawling: {url}")

            # Simulate Fetch
            content = self.fetch(url)

            # Extract Links
            for link in content:
                if link not in self.visited:
                    print(f"   found new link: {link}")
                    self.visited.add(link)
                    self.queue.append(link)

            time.sleep(0.5) # Politeness

    def fetch(self, url):
        return self.mock_internet.get(url, [])

if __name__ == "__main__":
    crawler = WebCrawler()
    print("Starting crawl from 'google.com'...")
    crawler.start_crawling("google.com")
```

**Output:**
```
Starting crawl from 'google.com'...
🕷️ Crawling: google.com
   found new link: gmail.com
   found new link: maps.google.com
🕷️ Crawling: gmail.com
🕷️ Crawling: maps.google.com
```

---

## 🧠 Interview Nuances

### 1. How to update older pages?
*   Use `Last-Modified` header.
*   Track "Change Rate": If a news site updates hourly, recrawl hourly. If a static blog updates yearly, recrawl yearly.

### 2. DNS Resolution Bottleneck?
*   DNS lookup can take 10ms - 200ms.
*   **Solution**: Maintain a dedicated DNS Cache (custom implementation, don't rely on OS cache) to keep millions of records.

### 3. Spider Traps?
*   Infinite URL structures like `calendar.com/2022/2023/2024...`.
*   **Fix**: Limit Max URL length. Limit Max Crawl Depth.

---

## ⚡ Flashcards
1.  **What is a URL Frontier?**
    *   The component that stores URLs to be crawled, prioritizing them based on importance and enforcing politeness (rate limits per domain).
2.  **Why use Bloom Filters in crawling?**
    *   To quickly check if a URL has already been visited with very low memory usage, avoiding infinite loops.
3.  **What is the 'Robots Exclusion Protocol'?**
    *   `robots.txt`. A standard used by websites to communicate with crawlers about which areas of the website should not be processed or scanned.
