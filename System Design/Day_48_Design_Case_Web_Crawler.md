# Day 48: Design Case - Web Crawler

## 🎯 Goal
Design a scalable Web Crawler (Google Bot) to index the entire internet.
**Scale**: 1 Billion pages/month.
Design a scalable web crawler to download and index the entire web (e.g., Googlebot).
**Focus**: URL Frontier, Politeness, Deduplication, and Parsing.

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start with seed URLs and follow links recursively.
2.  **Extract**: Parse HTML, extract text and links.
3.  **Store**: Save content to blob storage (S3) and metadata to DB.

### Non-Functional
1.  **Scalability**: Crawl 1 Billion pages/month.
2.  **Politeness**: Do not swamp a target server. Respect `robots.txt`.
3.  **Extensibility**: Support new content types (PDF, Images) later.
4.  **Robustness**: Handle malformed HTML, infinite loops, and spider traps.

---

## 📐 Capacity Estimation
*   **Pages**: 1 Billion pages / month.
*   **QPS**: 1B / (30 * 24 * 3600) ≈ **400 pages/sec**. (Very manageable).
*   **Storage**:
    *   Avg page size: 500KB.
    *   Total: 1B * 500KB = 500 TB/month.
    *   5 Years: **30 PB**.

---

## 🧠 Core Design Decisions

### 1. BFS vs DFS?
*   **DFS**: Might go too deep into one domain (spider trap).
*   **BFS**: Better coverage of diverse domains.
*   **Decision**: **BFS** using a priority queue (URL Frontier).

### 2. URL Frontier
*   Not just a simple Queue.
*   Needs to prioritize high-quality pages (PageRank).
*   Needs to ensure **Politeness** (don't hit `example.com` 100 times/sec).

### 3. Handling Duplicates
*   30% of web is duplicates.
*   **SimHash / Checksum**: Compute hash of content. If hash exists, discard.
*   **Bloom Filter**: Efficiently check if URL has already been visited.

### 4. DNS Resolution
*   DNS lookup is slow (10ms - 500ms).
*   **Solution**: Build a custom DNS Cache. Keep IP in memory to avoid repeated DNS queries.

---

## 🏗️ System Architecture

1.  **Seed URLs**: Entry point (e.g., cnn.com, wikipedia.org).
2.  **URL Frontier**: Manages the schedule.
    *   **Front Queue** (Prioritizer): Orders URLs by importance.
    *   **Back Queue** (Politeness): Maps URLs to a specific queue based on domain. One thread per domain queue.
3.  **HTML Downloader**: Fetches the page content.
    *   Checks **DNS Cache**.
    *   Checks **Robots.txt Cache**.
4.  **Content Parser**: Validates HTML, strips scripts.
5.  **Content Deduper**: Calculates checksum. Discards if duplicate.
6.  **URL Extractor**: Finds new links.
7.  **URL Deduper** (Bloom Filter): Discards if URL already in Frontier.
8.  **Storage**: Save to S3 (Content) and HBase (Metadata).

---

## 💻 Code Simulation: Simple Crawler Logic

Simulating the loop of fetching, parsing, and scheduling.

```python
import queue
import time
import threading
from urllib.parse import urlparse

class WebCrawler:
    def __init__(self):
        self.url_queue = queue.Queue()
        self.visited_urls = set()
        self.visited_lock = threading.Lock()

    def add_seed(self, url):
        self.url_queue.put(url)

    def is_visited(self, url):
        with self.visited_lock:
            return url in self.visited_urls

    def mark_visited(self, url):
        with self.visited_lock:
            self.visited_urls.add(url)

    def crawl(self, thread_id):
        while True:
            try:
                url = self.url_queue.get(timeout=2)

                if self.is_visited(url):
                    self.url_queue.task_done()
                    continue

                print(f"🕷️ [Thread-{thread_id}] Crawling: {url}")

                # simulate network delay
                time.sleep(1)

                # Mock Parsing: Assume every page links to a sub-page
                new_links = self.parse_links(url)

                self.mark_visited(url)

                for link in new_links:
                    if not self.is_visited(link):
                        self.url_queue.put(link)

                self.url_queue.task_done()

            except queue.Empty:
                break

    def parse_links(self, url):
        # Mock logic: generate 2 fake links
        base = urlparse(url).netloc
        return [f"http://{base}/page1", f"http://{base}/page2"]

if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.add_seed("http://example.com")
    crawler.add_seed("http://wikipedia.org")

    threads = []
    for i in range(3):
        t = threading.Thread(target=crawler.crawl, args=(i,))
        t.start()
        threads.append(t)

    for t in threads: t.join()

    print(f"✅ Crawling Complete. Visited {len(crawler.visited_urls)} pages.")
```

**Output:**
```
🕷️ [Thread-0] Crawling: http://example.com
🕷️ [Thread-1] Crawling: http://wikipedia.org
🕷️ [Thread-0] Crawling: http://example.com/page1
🕷️ [Thread-2] Crawling: http://example.com/page2
🕷️ [Thread-1] Crawling: http://wikipedia.org/page1
...
✅ Crawling Complete. Visited 6 pages.
```

---

## 🧠 Interview Nuances

### 1. Politeness Design
*   How to ensure we wait 1 second between requests to `cnn.com`?
*   Map `cnn.com` to Queue #5.
*   Worker #5 only reads from Queue #5.
*   Worker sleeps after processing a job.

### 2. Spider Traps
*   Infinite loops: `example.com/a/b/c/a/b/c...`
*   **Solution**: Limit max URL length. Limit max crawl depth.

### 3. Updating stale content?
*   How often to re-crawl?
*   Use `Last-Modified` header.
*   Prioritize dynamic sites (News) over static sites.

---

## ⚡ Flashcards
1.  **What is a Bloom Filter?**
    *   A probabilistic data structure used to test if an element is a member of a set. False positives are possible, false negatives are not. Used to check if URL visited.
2.  **Why use a custom DNS Cache?**
    *   Standard DNS lookups are synchronous and slow. A crawler needs high-throughput asynchronous resolution.
3.  **What is `robots.txt`?**
    *   A standard used by websites to communicate with web crawlers, specifying which areas of the website should not be processed or scanned.
