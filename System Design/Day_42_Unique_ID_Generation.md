# Day 42: Unique ID Generation

## 🎯 Goal
Understand how to generate globally unique identifiers in a distributed system where multiple servers are creating IDs simultaneously.
**Focus**: UUID vs Ticket Server vs Snowflake.

---

## 🧩 Key Concepts

### 1. Requirements
*   **Unique**: No two IDs can be the same.
*   **Sortable (Time-ordered)**: Preferable for databases (B-Tree locality).
*   **Numerical**: 64-bit integers are faster to index than strings.

### 2. Approaches

#### A. Database Auto-Increment
*   *Pros*: Simple.
*   *Cons*: Hard to scale (Sharding is messy). SPOF. Not globally unique across DBs.

#### B. UUID (Universally Unique Identifier)
*   *Format*: 128-bit string (e.g., `550e8400-e29b...`).
*   *Pros*: Zero coordination. Can be generated offline.
*   *Cons*: **Huge** (128 bits). **Not sortable**. Poor DB indexing performance (fragmentation).

#### C. Ticket Server (Flickr Strategy)
*   Centralized DB dedicated to handing out IDs ( `REPLACE INTO Tickets64 ...` ).
*   *Pros*: Numeric, Sortable.
*   *Cons*: SPOF. High latency (network call for every ID).

#### D. Twitter Snowflake (The Standard)
*   **Structure** (64 bits):
    *   1 bit: Sign (unused).
    *   41 bits: Timestamp (Milliseconds).
    *   10 bits: Machine ID (Data Center + Worker).
    *   12 bits: Sequence Number (For IDs generated in same millisecond).
*   *Pros*: Sortable (Time-based), Distributed (Worker ID), High Throughput (Sequence).

---

## 💻 Code Simulation: Snowflake Generator

A simplified Python implementation of Twitter's Snowflake.

```python
import time
import threading

class SnowflakeGenerator:
    def __init__(self, worker_id, datacenter_id):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0

        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12

        self.last_timestamp = -1

        # Shifts
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits

    def _current_millis(self):
        return int(time.time() * 1000)

    def next_id(self):
        timestamp = self._current_millis()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards!")

        if timestamp == self.last_timestamp:
            # Same millisecond, increment sequence
            self.sequence = (self.sequence + 1) & 4095 # 2^12 - 1
            if self.sequence == 0:
                # Sequence exhausted, wait for next millis
                while timestamp <= self.last_timestamp:
                    timestamp = self._current_millis()
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        # Construct ID
        id = ((timestamp << self.timestamp_shift) |
              (self.datacenter_id << self.datacenter_id_shift) |
              (self.worker_id << self.worker_id_shift) |
              self.sequence)
        return id

# Usage
gen = SnowflakeGenerator(worker_id=1, datacenter_id=1)
for _ in range(5):
    print(f"ID: {gen.next_id()}")
```

---

## ⚠️ The Trap: Clock Synchronization
*   **Problem**: Snowflake relies on `System Time`. If the server clock drifts or NTP rewinds time ("Leap Second"), you might generate duplicate IDs.
*   **The Fix**:
    1.  Check `if current_time < last_time`. Throw error or wait.
    2.  Use **Logical Clocks** (Lamport timestamps) if strict ordering is required, though standard Snowflake doesn't.

---

## ⚡ Flashcards
1.  **Why 41 bits for Timestamp?**
    *   $2^{41}$ milliseconds ≈ 69 years. We can use this format for 69 years from a custom Epoch (start date).
2.  **Why not use Random Numbers?**
    *   Collisions are possible (Birthday Paradox). Not sortable.
3.  **How many IDs can Snowflake generate per millisecond?**
    *   $2^{12} = 4096$ IDs per machine per millisecond. That's ~4 Million/sec per machine.
