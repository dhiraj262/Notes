# Day 37: Design Case - URL Shortener (TinyURL)

## 🎯 Goal
Design a system like Bit.ly or TinyURL that converts long URLs into short, unique aliases.
**Focus**: Back-of-the-envelope estimation, Unique ID generation, and Database choice.

---

## 🗣️ Requirements

### Functional
1.  **Shorten**: Given a long URL, generate a unique short alias (e.g., `bit.ly/AbCd12`).
2.  **Redirect**: Given a short alias, redirect the user to the original long URL (HTTP 301/302).
3.  **Custom Alias**: Allow users to pick their own alias (Optional).
4.  **Expiry**: Links expire after a default timespan (Optional).

### Non-Functional
1.  **Highly Available**: If the service is down, all links on the internet break.
2.  **Read-Heavy**: Write/Read ratio is likely 1:100 (1 person shares, 100 click).
3.  **Low Latency**: Redirection must be instant (< 200ms).

---

## 📐 Capacity Estimation (Back-of-the-Envelope)
*   **Write QPS**: Assume 100 Million new URLs per month.
    *   100M / (30 * 24 * 3600) ≈ **40 requests/sec**. (Very low).
*   **Read QPS**: 100:1 ratio -> **4,000 requests/sec**.
*   **Storage**:
    *   5 years. 100M * 12 * 5 = **6 Billion URLs**.
    *   Avg URL size = 500 bytes.
    *   Total Storage = 6B * 500B = 3TB. (Manageable on a single DB, but sharding helps).

---

## 🧠 Core Design Decisions

### 1. API Design
*   `POST /api/v1/data/shorten`
    *   Input: `{ "longUrl": "https://google.com/..." }`
    *   Output: `{ "shortUrl": "https://tiny.url/XyZ123" }`
*   `GET /{shortUrl}`
    *   Return: HTTP 301 Redirect. Location: `longUrl`.

### 2. Database Choice
*   **Relational (SQL)**? Good for structured data, but we don't need complex joins.
*   **NoSQL (DynamoDB/Cassandra)**? **Better**.
    *   High availability.
    *   Simple Key-Value access pattern (`ShortURL` -> `LongURL`).
    *   Easier to scale horizontally.

### 3. The Algorithm: How to generate the Alias?

#### Option A: Hashing (MD5/SHA)
*   Hash the long URL: `MD5("google.com")` -> `a1b2c3d4...`
*   Take first 7 chars.
*   *Problem*: **Collisions**. Two different URLs might have the same first 7 chars. Handling this is messy.

#### Option B: Base62 Conversion (Recommended)
*   Concept: Convert a unique integer ID (Database Auto-Increment ID) into Base62 (A-Z, a-z, 0-9).
*   Why Base62? 62 chars ^ 7 positions = 3.5 Trillion combinations. Enough for 6 Billion URLs.
*   **Flow**:
    1.  Get unique ID from a "Ticket Server" or DB (e.g., ID = 1000).
    2.  Convert 1000 to Base62 -> `g8`.
    3.  Short URL = `tiny.url/g8`.

---

## 🏗️ System Architecture

1.  **Client** sends `create(longUrl)`.
2.  **App Server** requests a unique ID from **KGS (Key Generation Service)**.
    *   *Note*: Using DB Auto-increment is risky (SPOF). A distributed "Snowflake" ID generator or a pre-generated key service is better.
3.  **KGS** returns `ID: 123456`.
4.  **App Server** converts `123456` -> Base62 `AbC`.
5.  **App Server** stores `{ "id": "AbC", "long_url": "..." }` in **NoSQL DB**.
6.  **App Server** returns `tiny.url/AbC`.

---

## 💻 Code Simulation: Base62 Encoder

```python
class Base62:
    CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @staticmethod
    def encode(num):
        if num == 0:
            return Base62.CHARSET[0]

        encoded = []
        while num > 0:
            rem = num % 62
            encoded.append(Base62.CHARSET[rem])
            num //= 62
        return "".join(reversed(encoded))

    @staticmethod
    def decode(s):
        num = 0
        for char in s:
            num = num * 62 + Base62.CHARSET.index(char)
        return num

# Simulation
db_id = 123456789
short_code = Base62.encode(db_id)
print(f"DB ID: {db_id} -> Short Code: {short_code}")

original_id = Base62.decode(short_code)
print(f"Short Code: {short_code} -> DB ID: {original_id}")

# Test Capacity
print(f"Max URLs with 7 chars: {62**7:,}")
```

---

## 🧠 Interview Nuances

### 301 vs 302 Redirect?
*   **301 (Permanent)**: Browser caches the redirection.
    *   *Pros*: Faster for user (no server hit next time).
    *   *Cons*: We lose analytics. We don't know if the user clicked it a 2nd time.
*   **302 (Temporary)**: Browser always hits our server first.
    *   *Pros*: Accurate analytics.
    *   *Cons*: Higher server load.
*   *Verdict*: Use 302 if Analytics > Performance. Use 301 otherwise.

### The "KGS" (Key Generation Service)
*   To avoid collision checks, we can pre-generate millions of 7-char keys and store them in a "Key DB".
*   Two tables: `Unused_Keys` and `Used_Keys`.
*   App Server fetches a batch of 1000 keys from `Unused_Keys` to memory (Buffer).
*   If App Server dies, we lose 1000 keys. Acceptable trade-off for speed.

---

## ⚡ Flashcards
1.  **What is a Bloom Filter used for here?**
    *   Quickly checking if a custom alias (e.g., "my-link") is already taken in the DB without doing a full disk read.
2.  **How to handle Expiry?**
    *   **Lazy Delete**: Do nothing. When user accesses, check timestamp. If expired, return error and delete.
    *   **Cron Job**: Periodic script running at night to clean up old entries.
