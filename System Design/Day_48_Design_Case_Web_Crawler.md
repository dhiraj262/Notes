# Day 48: Design Case - Web Crawler (Google Bot)

## 🎯 Goal
Design a scalable Web Crawler to fetch and index billions of web pages.
**Focus**: Politeness, Deduplication, and Scale.

---

## 🗣️ Requirements

### Functional
1.  **Seed URLs**: Start with a list of known URLs.
2.  **Recursive Crawling**: Extract links from pages and crawl them.
3.  **Storage**: Save HTML content for indexing.

### Non-Functional
1.  **Scale**: 10 Billion pages/month.
2.  **Politeness**: Don't bombard a single server. Respect `robots.txt`.
3.  **Extensibility**: Support different content types (HTML, PDF).

---

## 📐 Capacity Estimation
*   **Throughput**: 10B pages / 30 days ≈ 4000 pages/sec.
*   **Storage**:
    *   Avg page: 500KB.
    *   Total: 10B * 500KB = 5 Petabytes/month.
    *   Need tiered storage (S3 + Glacier).

---

## 🏗️ System Architecture

### 1. URL Frontier (The Scheduler)
*   **Prioritizer**: Decides which URL to crawl next (PageRank, frequency of updates).
*   **Politeness**: Ensures we don't hit `example.com` more than once per second.
    *   Queue Router: Maps `hostname` -> `Queue`.
    *   One queue per domain. One worker per queue.

### 2. HTML Downloader
*   Fetches the page.
*   DNS Resolver caching (Crucial for performance).

### 3. Deduplication (Content Fingerprinting)
*   **URL Filter**: Check if URL already visited (Bloom Filter).
*   **Content Filter**: Check if content is duplicate (SimHash / MinHash).
    *   If 2 URLs have identical content, store only one.

---

## 💻 Code Simulation: URL Frontier

Simulating the basic Frontier logic with deduplication.

```python
import queue
import hashlib

class WebCrawler:
    def __init__(self):
        self.url_frontier = queue.Queue()
        self.visited = set()

    def add_seed(self, url):
        self.url_frontier.put(url)

    def crawl(self):
        while not self.url_frontier.empty():
            url = self.url_frontier.get()

            # Deduplication
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in self.visited:
                print(f"🔄 Skipped (Visited): {url}")
                continue

            self.visited.add(url_hash)
            self.process_page(url)

    def process_page(self, url):
        print(f"🕷️ Crawling: {url}")
        # Simulate extracting links
        if url == "google.com":
            self.url_frontier.put("google.com/about")
            self.url_frontier.put("google.com/images")
        elif url == "google.com/about":
            self.url_frontier.put("google.com") # Cycle

if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.add_seed("google.com")
    crawler.crawl()
```

**Output:**
```
🕷️ Crawling: google.com
🕷️ Crawling: google.com/about
🕷️ Crawling: google.com/images
🔄 Skipped (Visited): google.com
```

---

## 🧠 Interview Nuances

### 1. How to handle infinite loops/Spider Traps?
*   Limit max URL length.
*   Limit max depth from seed.
*   Detect repeating patterns (`/gallery/foo/bar/foo/bar`).

### 2. DNS Resolution Bottleneck?
*   DNS is slow.
*   Crawler needs a dedicated DNS cache (not OS default) to keep millions of records.

### 3. Rendering JS (React/Angular)?
*   Standard request only gets HTML.
*   Need **Headless Chrome** (Puppeteer) to render dynamic sites. (Very expensive computationally).

---

## ⚡ Flashcards
1.  **What is Politeness in crawling?**
    *   The delay between requests to the same domain to avoid DOS-ing the server.
2.  **Bloom Filter use case?**
    *   Efficiently checking "Have I seen this URL before?" False positives possible, false negatives impossible.
3.  **SimHash?**
    *   A hashing algorithm where similar documents produce similar hashes (small Hamming distance). Used for near-duplicate detection.
