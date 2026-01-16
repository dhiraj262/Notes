# Day 48: Design a Web Crawler (Google Bot)

## 🎯 Goal
Design a scalable Web Crawler that collects, parses, and stores data from billions of web pages.

## 📋 Requirements

### Functional
1.  **Crawling**: Fetch web pages via HTTP.
2.  **Parsing**: Extract links (URL discovery).
3.  **Storage**: Save content (HTML/Text) for indexing.
4.  **Politeness**: Do not overwhelm servers. Respect `robots.txt`.

### Non-Functional
1.  **Scalability**: Fetch billions of pages per month.
2.  **Robustness**: Handle malformed HTML, dead links, infinite loops.
3.  **Extensibility**: Support new content types (PDF, Images).

## 🔢 Capacity Estimation

*   **Scale**: 1 Billion URLs to crawl.
*   **Average Size**: 500 KB per page.
*   **Throughput**:
    *   Target: 1 Billion / 30 days $\approx$ 400 requests/sec. (Seems low? A real crawler targets far more). Let's aim for **5,000 QPS**.
*   **Storage**: $10^9 \times 500 \text{KB} = 500 \text{TB}$. Compressed $\approx 150 \text{TB}$.

## 🏗️ Architecture Design

### 1. URL Frontier (The Queue)
The brain of the crawler. It prioritizes which URLs to crawl next.
*   **Frontier Queue**: Not a simple FIFO.
*   **Prioritization**: High-quality/fresh content first (PageRank logic).
*   **Politeness**: Enforce a delay between requests to the same domain.
    *   *Implementation*: `Map<Host, Queue>`. A "Mapping Table" assigns domains to queues. A "Queue Selector" picks a queue that hasn't been touched in $X$ seconds.

### 2. DNS Resolver
DNS lookup is slow (20ms - 500ms).
*   **Bottleneck**: Standard OS DNS is synchronous.
*   **Solution**: Build a custom, high-performance **DNS Cache** that runs asynchronously.

### 3. Duplicate Detection
Don't crawl the same page twice.
*   **Content Dedup**: Compare content hashes (MD5/SHA).
*   **URL Dedup**: Has this URL been seen?
    *   **Bloom Filter**: Space-efficient probabilistic set. "Possibly in set" or "Definitely not".
    *   10 Billion URLs $\times$ 1 bit $\approx$ 1.2 GB RAM. Feasible.

### 4. HTML Fetcher & Parser
*   **Fetcher**: Workers that download content. Use Python `requests` or Go `http`.
*   **Parser**: Validate HTML, extract links, fix relative URLs.

## 🐍 Code Simulation
Python simulation of a **Bloom Filter** integrated into a simple crawl loop.

```python
import hashlib
from collections import deque

class BloomFilter:
    def __init__(self, size=1000, hash_count=3):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size

    def _hashes(self, item):
        # Generate multiple hashes (simulated using salt)
        hashes = []
        for i in range(self.hash_count):
            h = int(hashlib.md5((item + str(i)).encode('utf-8')).hexdigest(), 16)
            hashes.append(h % self.size)
        return hashes

    def add(self, item):
        for h in self._hashes(item):
            self.bit_array[h] = 1

    def check(self, item):
        for h in self._hashes(item):
            if self.bit_array[h] == 0:
                return False
        return True # Probably present

class WebCrawler:
    def __init__(self):
        self.url_frontier = deque() # Queue of URLs to visit
        self.bloom_filter = BloomFilter()
        self.storage = {} # url -> content

    def add_seed(self, url):
        self.url_frontier.append(url)
        self.bloom_filter.add(url)

    def crawl(self, limit=5):
        count = 0
        while self.url_frontier and count < limit:
            url = self.url_frontier.popleft()

            # 1. Fetch
            content = self._fetch_url(url)
            self.storage[url] = content
            print(f"[Crawl] Visited: {url} | Found {len(content)} bytes")

            # 2. Parse & Extract Links (Mocking links)
            extracted_links = self._parse_links(url)

            # 3. Filter & Add to Frontier
            for link in extracted_links:
                if not self.bloom_filter.check(link):
                    self.bloom_filter.add(link)
                    self.url_frontier.append(link)
                    print(f"   -> Enqueued new link: {link}")
                else:
                    print(f"   -> Skipped duplicate/visited: {link}")

            count += 1

    def _fetch_url(self, url):
        # Mock fetch
        return f"<html>Content of {url}</html>"

    def _parse_links(self, url):
        # Mock logic: page1 links to page2, etc.
        if url == "google.com":
            return ["google.com/images", "google.com/maps", "yahoo.com"]
        if url == "yahoo.com":
            return ["yahoo.com/news", "google.com"] # google.com is dupe
        return []

# --- Driver Code ---
if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.add_seed("google.com")
    crawler.crawl()
```

## 🧠 Interview Nuances

### "The Trap": Infinite Loops & Spider Traps
*   **Problem**: `example.com/a/b/c/d/...` dynamically generated paths.
*   **Solution**: Limit **Max URL Depth** (e.g., 10 hops from seed). Limit **Max Pages per Domain**.

### "The Kill Shot": Content Deduplication
*   **Challenge**: "Two pages have different HTML but same content (ads differ)."
*   **Solution**: **SimHash**.
    *   A "Locality Sensitive Hashing" (LSH) technique.
    *   Standard Hash: `Hash(A) != Hash(B)` if A and B differ by 1 bit.
    *   SimHash: `SimHash(A)` is *close* to `SimHash(B)` (Hamming distance) if text is similar.

### "Production Realities"
*   **Dynamic Rendering**: Many sites use React/Angular (Client Side Rendering). The initial HTML is empty.
*   **Solution**: The crawler must run a Headless Browser (Puppeteer/Selenium) to render JS, which is $100\times$ slower and more expensive than raw HTML fetching.

## ⚡ Flashcards
*   **URL Dedup?** -> Bloom Filter.
*   **Content Dedup?** -> SimHash / Shingling.
*   **Politeness?** -> Delay queues per domain.
*   **Trap Prevention?** -> Max Depth + URL pattern regex.
