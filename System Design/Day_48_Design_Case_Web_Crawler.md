# Day 48: Design Case - Web Crawler

## 🎯 Goal
Design a scalable Web Crawler (Google Bot) to index the entire internet.
**Scale**: 1 Billion pages/month.

---

## 🗣️ Requirements

### Functional
1.  **Crawl**: Start from seed URLs, fetch content, extract links, repeat.
2.  **Politeness**: Do not hammer a website. Respect `robots.txt`.
3.  **Content**: Store HTML for indexing.

### Non-Functional
1.  **Scalability**: Must be distributed (The web is huge).
2.  **Robustness**: Handle bad HTML, infinite loops, and server errors.
3.  **Extensibility**: Support new content types (Images, PDFs).

---

## 📐 Capacity Estimation
*   **Pages**: 1 Billion/month = ~400/sec (Seems low, let's target **10k pages/sec** for a real crawler).
*   **Storage**:
    *   Avg page size: 500KB.
    *   1B pages * 500KB = 500 TB/month.
    *   5 years = 30 PB. (Need S3/HDFS).

---

## 🧠 Core Design Decisions

### 1. BFS vs DFS?
*   **BFS (Breadth-First Search)**: Usually better. We want to cover many domains, not go deep into one immediately (which might look like an attack).
*   **DFS**: Good for "vertical" crawling, but bad for politeness.

### 2. URL Frontier (The Manager)
*   The component that decides "What to crawl next?".
*   **Priority Queue**: Crawl high-rank pages (PageRank) more often.
*   **Politeness Queue**: Ensure we don't send 100 requests/sec to `cnn.com`. Map `hostname` to a specific worker thread with a delay.

### 3. Duplicate Detection
*   30% of the web is duplicate content.
*   **URL Dedupe**: Bloom Filter or Hash Check (MD5 of URL).
*   **Content Dedupe**: SimHash or Checksum of HTML content to detect "Same content, different URL".

---

## 🏗️ System Architecture

1.  **Seed URLs**: Input list.
2.  **URL Frontier**:
    *   **Front Queue (Prioritizer)**: Assigns priority (1-10).
    *   **Back Queue (Politeness)**: Maps Hostname -> Worker. Enforces delays.
3.  **HTML Fetcher**: Downloads page. Checks DNS Cache.
4.  **Content Parser**: Validates HTML. Extracts Links.
5.  **Dedup Service**: Checks Bloom Filter. If new, add to storage.
6.  **Storage**: S3 (HTML), SQL (Metadata).
7.  **Loop**: Extracted links go back to URL Frontier.

---

## 💻 Code Simulation: Simple Crawler

Simulating the core loop: Frontier -> Fetch -> Parse -> Dedupe.

```python
import queue
import time
import random

class WebCrawler:
    def __init__(self):
        self.url_frontier = queue.Queue()
        self.visited_urls = set()
        self.dns_cache = {} # Host -> IP

    def add_seed(self, url):
        self.url_frontier.put(url)
        self.visited_urls.add(url)

    def is_allowed(self, url):
        # Mock Robots.txt check
        if "forbidden" in url:
            print(f"🚫 Blocked by Robots.txt: {url}")
            return False
        return True

    def resolve_dns(self, url):
        host = url.split("/")[0]
        if host not in self.dns_cache:
            # Simulate DNS lookup
            self.dns_cache[host] = f"192.168.1.{random.randint(1, 255)}"
        return self.dns_cache[host]

    def crawl(self):
        while not self.url_frontier.empty():
            url = self.url_frontier.get()

            if not self.is_allowed(url):
                continue

            ip = self.resolve_dns(url)
            print(f"🕷️ Crawling: {url} (IP: {ip})")

            # Simulate processing time
            # time.sleep(0.1)

            # Mock Parsing HTML and finding new links
            new_links = self.extract_links(url)

            for link in new_links:
                if link not in self.visited_urls:
                    self.visited_urls.add(link)
                    self.url_frontier.put(link)
                    print(f"   ➕ Found new link: {link}")

    def extract_links(self, url):
        # Mock link extraction logic
        if url == "google.com":
            return ["google.com/images", "google.com/maps", "evil-site.com/forbidden"]
        elif url == "google.com/images":
            return ["google.com/cat.jpg"]
        return []

if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.add_seed("google.com")

    print("--- Starting Crawl ---")
    crawler.crawl()
    print("--- Crawl Finished ---")
```

**Output:**
```
--- Starting Crawl ---
🕷️ Crawling: google.com (IP: 192.168.1.80)
   ➕ Found new link: google.com/images
   ➕ Found new link: google.com/maps
   ➕ Found new link: evil-site.com/forbidden
🕷️ Crawling: google.com/images (IP: 192.168.1.80)
   ➕ Found new link: google.com/cat.jpg
🕷️ Crawling: google.com/maps (IP: 192.168.1.80)
🚫 Blocked by Robots.txt: evil-site.com/forbidden
🕷️ Crawling: google.com/cat.jpg (IP: 192.168.1.80)
--- Crawl Finished ---
```

---

## 🧠 Interview Nuances

### 1. How to handle "Spider Traps"?
*   Infinite loop: `website.com/a/b/a/b...`.
*   **Solution**: Limit max URL length. Limit max directory depth. Check for cycling patterns.

### 2. DNS is a bottleneck?
*   DNS resolution takes time (20ms-500ms).
*   **Solution**: Build a custom DNS Caching Server. Keep the cache updated aggressively.

### 3. Updating stale content?
*   How often to re-crawl `cnn.com`?
*   Use `Last-Modified` header. Learn the update frequency pattern (Adaptive Recrawl).

---

## ⚡ Flashcards
1.  **What is `robots.txt`?**
    *   A standard file that tells crawlers which parts of the site they are NOT allowed to visit.
2.  **What is a Bloom Filter used for here?**
    *   To quickly check if a URL has already been visited (Space efficient, but has false positives).
3.  **Why use Consistent Hashing in a Crawler?**
    *   To distribute hostnames across different download workers. E.g., `google.com` always goes to Worker 1, `yahoo.com` to Worker 2.
