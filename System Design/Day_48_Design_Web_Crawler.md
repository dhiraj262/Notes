# Day 48: Design a Web Crawler (Google Search)

## 🎯 Goal
Design a scalable crawler that downloads billions of web pages to index them.
**Focus**: URL Frontier, Politeness, Deduplication, and Parsing.

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start from seed URLs and discover links.
2.  **Store**: Save content to Blob Store (S3).
3.  **Extensibility**: Support HTML, PDF, Images.

### Non-Functional
1.  **Scale**: 1 Billion pages/month.
2.  **Politeness**: Do not overload target servers. Respect `robots.txt`.
3.  **Freshness**: Re-crawl frequently updated pages.

---

## 📐 Capacity Estimation
*   **Pages**: 1 Billion / month.
*   **QPS**: 1B / 30 days / 24h / 3600s ≈ 400 pages/sec.
*   **Storage**: Avg 100KB/page -> 100TB / month. 5 Years = 6PB.
*   **Bandwidth**: 400 * 100KB = 40 MB/s.

---

## 🧠 Core Design Decisions

### 1. URL Frontier (The Queue)
*   Need to prioritize URLs (PageRank, Freshness) and ensure Politeness (Per-domain queues).
*   **Architecture**:
    *   **Prioritizer**: Splits URLs into F1 (High Priority) to Fk.
    *   **Queue Router**: Maps URL to a queue based on *Domain*.
    *   **Mapping Table**: Domain A -> Queue 1.

### 2. DNS Resolution
*   Bottleneck! DNS is slow (10ms-500ms).
*   **Solution**: Build a custom high-performance DNS Cache.

### 3. Deduplication (Content)
*   30% of web pages are duplicates.
*   Use **SimHash** or **Bloom Filters** on content to detect near-duplicates.

---

## 🏗️ System Architecture

1.  **Seed URLs**: The starting point.
2.  **URL Frontier**: Feeds URLs to workers.
3.  **HTML Downloader**: Fetches the page. Uses DNS Resolver.
4.  **Content Parser**: Validates HTML. Malformed? Discard.
5.  **Dup Detector**: Checks fingerprint against DB.
6.  **URL Extractor**: Finds `<a>` tags.
7.  **URL Filter/Normalizer**: Removes ads, converts relative paths to absolute.
8.  **Robots.txt Cache**: Checks permission.

---

## 💻 Code Simulation: Politeness & Frontier

Simulating a crawler that respects domain politeness.

```python
import threading
import queue
import time
from urllib.parse import urlparse

class WebCrawler:
    def __init__(self):
        self.url_frontier = queue.Queue()
        self.visited_urls = set()
        self.visited_lock = threading.Lock()
        self.domain_last_visit = {} # Politeness: domain -> timestamp

    def add_seed(self, url):
        self.url_frontier.put(url)

    def is_visited(self, url):
        with self.visited_lock:
            if url in self.visited_urls:
                return True
            self.visited_urls.add(url)
            return False

    def is_polite(self, domain):
        # Enforce 0.5 second delay per domain
        last_time = self.domain_last_visit.get(domain, 0)
        if time.time() - last_time < 0.5:
            return False
        return True

    def crawl(self):
        while True:
            try:
                url = self.url_frontier.get(timeout=1)
            except queue.Empty:
                break

            domain = urlparse(url).netloc

            # Politeness check
            if not self.is_polite(domain):
                # Put back in queue to retry later
                self.url_frontier.put(url)
                continue

            if self.is_visited(url):
                self.url_frontier.task_done()
                continue

            print(f"🕷️ Crawling: {url}")
            self.domain_last_visit[domain] = time.time()

            # Mock extracting links
            self.extract_links(url)
            self.url_frontier.task_done()

    def extract_links(self, url):
        # Mocking link extraction
        if url == "http://google.com":
            self.add_seed("http://google.com/images")
            self.add_seed("http://google.com/maps")
        elif url == "http://cnn.com":
            self.add_seed("http://cnn.com/news")

if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.add_seed("http://google.com")
    crawler.add_seed("http://cnn.com")

    # Start threads
    t1 = threading.Thread(target=crawler.crawl)
    t1.start()
    t1.join()
```

**Output:**
```
🕷️ Crawling: http://google.com
🕷️ Crawling: http://cnn.com
🕷️ Crawling: http://google.com/images
🕷️ Crawling: http://cnn.com/news
...
```

---

## 🧠 Interview Nuances

### 1. How to handle Spider Traps?
*   Infinite loops like `calendar.com/2020/2021/2022...`.
*   **Fix**: Max URL length, max directory depth, cycle detection.

### 2. Rendered pages (React/Angular)?
*   Simple HTTP GET won't work.
*   Need **Headless Chrome** (Puppeteer/Selenium) to render JS. Extremely expensive (10x slower).

### 3. Checksums?
*   MD5 is good for exact match.
*   **SimHash** is needed for "Near Duplicate" (e.g., page changed date but content is same).

---

## ⚡ Flashcards
1.  **What is a URL Frontier?**
    *   The data structure (queues) that manages which URLs to crawl next, handling priority and politeness.
2.  **What is robots.txt?**
    *   A file on a website telling crawlers which parts are allowed/disallowed.
3.  **Why use Consistent Hashing for a Crawler?**
    *   To assign domains to downloaders. If `google.com` maps to Node A, only Node A downloads from Google (easier to manage politeness).
