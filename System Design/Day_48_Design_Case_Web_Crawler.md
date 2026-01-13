# Day 48: Design Case - Web Crawler (Googlebot)

## 🎯 Goal
Design a scalable web crawler to download and index billions of web pages.
**Focus**: Politeness, URL Frontier, and Duplicate Detection.

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start from seed URLs and discover links.
2.  **Parse**: Extract text and links from HTML.
3.  **Store**: Save content to blob storage for indexing.

### Non-Functional
1.  **Scalability**: Crawl 1 Billion pages per month.
2.  **Politeness**: Do not hammer a single server (Respect `robots.txt`).
3.  **Extensibility**: Support HTML, PDF, Images.
4.  **Robustness**: Handle spider traps (infinite loops), malformed HTML.

---

## 📐 Capacity Estimation
*   **Target**: 1 Billion pages / month.
*   **QPS**: $10^9 / (30 \times 24 \times 3600) \approx 400$ pages/sec.
*   **Peak**: 1000 pages/sec.
*   **Storage**: Avg page 500KB.
    *   $10^9 \times 500 \text{KB} = 500 \text{TB} / \text{month}$.
    *   5 Years = 30 PB.

---

## 🧠 Core Design Decisions

### 1. BFS vs DFS
*   **DFS**: Might get stuck in a deep path (Spider Trap) on one domain.
*   **BFS**: Breadth-First Search is better. Crawls level by level, discovering diverse domains.

### 2. URL Frontier (The Queue)
*   Ideally, a simple Queue.
*   **Problem**: If we pop 100 URLs from `wikipedia.org` consecutively, we DDoS Wikipedia.
*   **Solution**: **Politeness Queue**.
    *   Map `hostname` -> `Queue`.
    *   Worker threads pick a hostname queue and process it with a delay (e.g., 1 sec between requests).

### 3. Duplicate Detection
*   **URL Level**: Have we seen `google.com/a`?
    *   Use **Bloom Filter** (Space efficient) or Redis Set.
*   **Content Level**: Is Page A same as Page B? (Mirror sites).
    *   Compute **SimHash** or Checksum (MD5) of content. If checksum exists, discard.

### 4. DNS Resolution
*   DNS lookup is slow (10ms - 500ms).
*   **Solution**: Build a custom **DNS Cache** server to avoid repeated lookups for the same domain.

---

## 🏗️ System Architecture

1.  **Seed URLs**: Input list (e.g., cnn.com, bbc.com).
2.  **URL Frontier**:
    *   **Prioritizer**: Which URL is important? (PageRank).
    *   **Politeness**: Ensures delay between hits to same domain.
3.  **HTML Fetcher**:
    *   Downloads page.
    *   Checks `Robots.txt`.
4.  **Content Parser**: Validates HTML/PDF.
5.  **Duplicate Eliminator**: Checks Checksum.
6.  **URL Extractor**: Finds `<a>` tags.
7.  **URL Filter**: Discards ads, blacklisted sites.
8.  **Storage**: Save to S3/HDFS.

---

## 💻 Code Simulation: Politeness & Frontier

Simulating the logic of a polite crawler.

```python
import queue
import time
import threading

class WebCrawler:
    def __init__(self):
        # In-memory URL Frontier
        self.url_queue = queue.Queue()
        self.visited = set()

        # Domain Politeness: domain -> last_access_timestamp
        self.domain_access_times = {}
        self.min_delay = 1.0 # 1 second delay per domain

    def add_url(self, url):
        if url not in self.visited:
            self.visited.add(url)
            self.url_queue.put(url)

    def is_polite(self, domain):
        last_time = self.domain_access_times.get(domain, 0)
        if time.time() - last_time < self.min_delay:
            return False
        return True

    def crawl(self):
        while not self.url_queue.empty():
            url = self.url_queue.get()
            domain = url.split("/")[0] # Mock domain extraction

            if not self.is_polite(domain):
                # Put back in queue to try later
                self.url_queue.put(url)
                time.sleep(0.1)
                continue

            self.process_page(url, domain)

    def process_page(self, url, domain):
        self.domain_access_times[domain] = time.time()
        print(f"🕷️ Fetched: {url}")

        # Mock extracting links
        if len(url) < 20:
            self.add_url(f"{url}/a")
            self.add_url(f"{url}/b")

if __name__ == "__main__":
    bot = WebCrawler()
    bot.add_url("google.com")
    bot.add_url("wiki.org")

    # Run in a thread to simulate background work
    t = threading.Thread(target=bot.crawl)
    t.start()

    # Stop after 2 seconds for demo
    time.sleep(2)
    # (In real code we'd have a stop flag)
```

**Output:**
```
🕷️ Fetched: google.com
🕷️ Fetched: wiki.org
🕷️ Fetched: google.com/a
🕷️ Fetched: google.com/b
... (Interleaved or delayed if same domain)
```

---

## 🧠 Interview Nuances

### 1. Handling Updates
*   How often to re-crawl?
*   **Strategy**: Exponential decay. If page changes often, crawl often. If not, reduce frequency. Use `Last-Modified` header.

### 2. Spider Traps
*   `example.com/a/b/c/d/e/...` infinite directory.
*   **Fix**: Limit URL length (e.g., max 100 chars). Limit path depth (max 10 slashes).

### 3. Server-Side Rendering (SSR) vs Client-Side (CSR)
*   Standard crawler sees empty page if site uses React/Angular without SSR.
*   **Fix**: Use a Headless Browser (Puppeteer/Selenium) to render JS. (Expensive/Slow).

---

## ⚡ Flashcards
1.  **What is `robots.txt`?**
    *   Standard file at root of site (`site.com/robots.txt`) telling crawlers which paths NOT to visit.
2.  **Consistent Hashing in Crawler?**
    *   Used to distribute URLs to Downloader machines based on hostname. Ensures all URLs from `cnn.com` go to Worker A (easier politeness enforcement).
3.  **Bloom Filter False Positive?**
    *   If Bloom Filter says "URL Seen", it might be wrong (False Positive). We skip a valid page. Acceptable trade-off for memory saving.
