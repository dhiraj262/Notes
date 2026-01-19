# Day 48: Design a Web Crawler (Googlebot)

## 🎯 Goal
Design a scalable crawler to fetch, parse, and index billions of web pages.
**Focus**: Politeness, URL Frontier, and Handling Cycles.

---

## 🗣️ Requirements

### Functional
1.  **Seed URLs**: Start with a list of known URLs.
2.  **Crawling**: Fetch HTML, extract links, add to queue.
3.  **Storage**: Save content for the Indexer.
4.  **Politeness**: Do not hammer a single server. Respect `robots.txt`.

### Non-Functional
1.  **Scale**: 1 Billion pages/month.
2.  **Extensibility**: Handle different content types (HTML, PDF, Images).
3.  **Robustness**: Handle bad HTML, malformed links, infinite loops (spider traps).

---

## 📐 Capacity Estimation
*   **Fetch Rate**: 1 Billion / 30 days ≈ 400 requests/sec. (Low avg, but peak is higher).
*   **Storage**: 1B pages * 100KB = 100 TB/month. -> 6 PB/ 5 years.
*   **Time**: fetching 1B pages with 1 machine is impossible. Need distributed workers.

---

## 🧠 Core Design Decisions

### 1. The URL Frontier (The Brain)
*   **Function**: Prioritizes URLs and ensures politeness.
*   **Architecture**:
    *   **Prioritizer**: Which URL is important? (PageRank logic).
    *   **Politeness Enforcer**: Ensures we don't send 100 req/sec to `cnn.com`.
    *   **Implementation**: A set of Queues. Each queue maps to ONE domain (e.g., `Queue_CNN`, `Queue_Wiki`). A worker thread binds to one queue at a time to enforce delay.

### 2. DNS Resolution
*   DNS lookup (10ms - 500ms) is a bottleneck.
*   *Solution*: Build a custom **DNS Cache** that keeps millions of IP addresses in memory.

### 3. Duplicate Detection
*   30% of web is duplicate.
*   **SimHash / Checksum**: Compute a 64-bit hash of page content. If seen before, discard.

---

## 🏗️ System Architecture

1.  **Seed URLs**: Input list.
2.  **URL Frontier**: Manages queues.
3.  **HTML Downloader**: Fetches page.
4.  **DNS Resolver**: Caches IPs.
5.  **Content Parser**: Validates HTML, extracts links.
6.  **Dedup Service**: Checks content fingerprint.
7.  **URL Filter**: Checks `robots.txt` and Blacklist.
8.  **Link Extractor**: Finds new URLs -> Sends back to Frontier.

### The Politeness Flow
1.  Frontier has 1000 queues (one per domain).
2.  Worker asks Frontier for work.
3.  Frontier checks: "Is `cnn.com` queue free? Was last request > 1s ago?"
4.  If Yes -> Pop URL -> Give to Worker.
5.  If No -> Check next queue.

---

## 💻 Code Simulation: URL Frontier (Politeness)

Simulating the Round-Robin logic to ensure we don't bombard a single domain.

```python
import urllib.parse
import collections

class URLFrontier:
    def __init__(self):
        # Maps domain -> queue of URLs
        self.queues = collections.defaultdict(collections.deque)
        self.seen_urls = set()

    def add_url(self, url):
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        # Extract domain
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc

        # Add to domain-specific queue
        self.queues[domain].append(url)
        print(f"📥 Added: {url} (Domain: {domain})")

    def get_next_url(self):
        # Round Robin selector (Simple Politeness)
        if not self.queues:
            return None

        # Get list of domains
        domains = list(self.queues.keys())

        # In a real system, we would track "last_access_time" per domain here.
        for domain in domains:
            if self.queues[domain]:
                url = self.queues[domain].popleft()
                # Clean up empty queues
                if not self.queues[domain]:
                    del self.queues[domain]
                return url
        return None

if __name__ == "__main__":
    frontier = URLFrontier()

    # Simulate seeding
    frontier.add_url("http://google.com/about")
    frontier.add_url("http://google.com/images")
    frontier.add_url("http://facebook.com/login")
    frontier.add_url("http://twitter.com/home")
    frontier.add_url("http://facebook.com/profile")

    print("\n🚀 Starting Crawl (Politeness enforced via Round Robin)...")

    # Fetch 5 times. Notice how it alternates domains if implemented with proper heap/RR.
    # Here we just iterate keys, which approximates round robin.
    for i in range(5):
        url = frontier.get_next_url()
        if url:
            parsed = urllib.parse.urlparse(url)
            print(f"🕷️ Crawling: {url} (Domain: {parsed.netloc})")
```

---

## 🧠 Interview Nuances

### 1. How to handle Spider Traps?
*   **Infinite Loop**: `site.com/a/b/c/d/e/...`
*   **Fix**: Limit URL length. Limit "Maximum Depth" (hops from seed). Detect cycles in graph.

### 2. Client-Side Rendering (React/Angular)?
*   Standard crawler only sees `<div id="app"></div>`.
*   **Fix**: Use a **Headless Browser** (Puppeteer/Selenium) to render JS. Costs 10x more CPU.

### 3. Updating Stale Content?
*   How often to recrawl `bbc.com` vs `static-site.com`?
*   Use an **Adaptive Schedule**. If page changed last time, shorten interval. If not, increase interval (exponential backoff).

---

## ⚡ Flashcards
1.  **What is robots.txt?**
    *   A standard file at the root of a site (e.g., `google.com/robots.txt`) telling crawlers which paths are allowed/disallowed.
2.  **BFS vs DFS for Crawling?**
    *   **BFS** (Breadth-First Search) is better. It explores the breadth of the web (high-quality pages are usually shallow). DFS might get stuck in a deep branch (spider trap).
3.  **Bloom Filter use case?**
    *   Used in the Frontier to quickly check if a URL has already been visited (Space efficient set).
