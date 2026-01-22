# Day 48: Design Case - Distributed Web Crawler

## 🎯 Goal
Design a crawler to index the web (GoogleBot) or archive it (Internet Archive).

---

## 🗣️ Requirements

### Functional
1.  **Seed URLs**: Start with known sites (e.g., CNN, BBC).
2.  **HTML Parsing**: Extract text and links.
3.  **Storage**: Store metadata (DB) and content (Blob).
4.  **Politeness**: Don't DoS a website. Respect `robots.txt`.

### Non-Functional
1.  **Scalability**: Fetch 1 Billion pages/week.
2.  **Extensibility**: Support new content types (PDF, Images) later.
3.  **Robustness**: Handle malformed HTML, infinite loops, and crash cycles.

---

## 📐 Capacity Estimation
*   **Target**: 1 Billion pages/month = ~400 req/sec (Average).
*   **Peak**: 2-3k req/sec.
*   **Storage**: 1B pages * 100KB = 100 TB/month. 5 Years = 6 PB.
*   **Parsing**: CPU intensive.

---

## 🧠 Core Design Decisions

### 1. The URL Frontier
*   The "Brain" of the crawler. Tells workers *what* to crawl next.
*   **Problem**: Simple FIFO queue makes us spam one domain (e.g., fetching 10k wikipedia pages in a row).
*   **Solution**: **Politeness Queue**.
    *   Map `Domain -> Queue`.
    *   Worker ensures `delay` between requests to the same domain.

### 2. Duplicate Detection
*   We don't want to crawl the same page twice.
*   **Bloom Filter**: Check `visited_urls`.
*   **Checksum**: MD5/SHA signature of the *content* to detect duplicates with different URLs.

### 3. DNS Resolution
*   DNS lookup is slow (10ms - 500ms).
*   **Solution**: Build a custom **DNS Cache** that keeps IPs in memory to avoid repeated lookups.

---

## 🏗️ System Architecture

1.  **Seed URLs** -> **URL Frontier**.
2.  **URL Frontier**:
    *   Prioritizes URLs (PageRank).
    *   Enforces Politeness.
    *   Assigns batch of URLs to Workers.
3.  **HTML Downloader (Worker)**:
    *   Checks **Robots.txt** Cache.
    *   Fetches Page (DNS Cache).
4.  **Content Parser**:
    *   Validates HTML.
    *   Extracts Links -> Sends to **URL Filter**.
    *   Extracts Text -> Sends to **Indexer/Storage**.
5.  **URL Filter**:
    *   Checks **Bloom Filter** ("Have we seen this?").
    *   If New: Add to **URL Frontier**.

---

## 💻 Code Simulation: Politeness Frontier

Simulates a crawler that respects domain-level delays.

```python
import queue
import time
import urllib.parse

class WebCrawler:
    def __init__(self):
        self.frontier = queue.Queue()
        self.visited = set()
        self.politeness_delay = 0.5 # seconds
        self.domain_last_visit = {} # {domain: timestamp}

    def add_url(self, url):
        if url not in self.visited:
            self.frontier.put(url)
            self.visited.add(url) # Mark as seen
            print(f"➕ Added to Frontier: {url}")

    def is_polite(self, domain):
        last = self.domain_last_visit.get(domain, 0)
        return (time.time() - last) > self.politeness_delay

    def crawl(self):
        print("\n🕷️ Starting Crawl...")
        while not self.frontier.empty():
            url = self.frontier.get()
            domain = urllib.parse.urlparse(url).netloc

            # Politeness Check
            while not self.is_polite(domain):
                time.sleep(0.1)

            # Mock Fetch
            print(f"📥 Fetching: {url}")
            self.domain_last_visit[domain] = time.time()

            # Mock Parsing (extract links)
            new_links = self.parse_html(url)
            for link in new_links:
                self.add_url(link)

    def parse_html(self, url):
        # Mocking link extraction based on current URL
        if url == "http://google.com":
            return ["http://google.com/mail", "http://google.com/maps"]
        elif url == "http://google.com/maps":
            return ["http://google.com/maps/place/1"]
        return []

# Simulation Usage
if __name__ == "__main__":
    crawler = WebCrawler()

    # Seed
    crawler.add_url("http://google.com")
    crawler.add_url("http://yahoo.com") # Should interleave nicely

    crawler.crawl()
```

---

## 🧠 Interview Nuances

### 1. How to handle Spider Traps?
*   **Infinite Deep Links**: `calendar.com/2020/01`, `/2020/02`...
*   **Solution**: Set a **Max Depth** limit (e.g., 20 hops from seed).

### 2. How to handle Dynamic Content (React/Angular)?
*   Standard HTTP requests only get the initial HTML shell.
*   **Solution**: Use a **Headless Browser** (Puppeteer/Selenium) to render JS. (Expensive, so do it selectively).

### 3. Distributed Frontier?
*   Use Kafka to partition URLs by hostname.
*   Worker 1 handles `*.google.com`, Worker 2 handles `*.yahoo.com`. This naturally enforces politeness (one worker per domain).

---

## ⚡ Flashcards
1.  **What is robots.txt?**
    *   A file on a website (e.g., `google.com/robots.txt`) that tells crawlers which paths they are allowed/disallowed to visit.
2.  **Why use a Bloom Filter here?**
    *   To check if a URL exists in a set of billions of URLs with very little memory. It might give a False Positive (saying "Seen" when new), but never a False Negative.
3.  **DFS vs BFS for Crawling?**
    *   **BFS** (Breadth-First) is better. DFS might get stuck deep in one domain (Spider Trap). BFS explores neighbors first (better variety).
