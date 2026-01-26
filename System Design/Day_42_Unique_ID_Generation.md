# Day 42: Unique ID Generation

## 🎯 Goal
Understand how to generate globally unique identifiers in a distributed system without coordination.
**Focus**: Twitter Snowflake vs UUID vs DB Auto-Increment.

---

## 🧩 Key Concepts

### 1. The Challenge
We need a Primary Key for every row/entity.
*   **Requirements**: Unique, Sortable by time (usually), Numerical (for performance).
*   **Problem**: In a distributed system with 100 database nodes, how do you ensure Node A and Node B don't generate ID `101` at the same time?

### 2. Solutions

#### A. Database Auto-Increment
*   **Mechanism**: `id SERIAL PRIMARY KEY`.
*   **Pros**: Simple, numerical.
*   **Cons**:
    *   **SPOF**: One DB controls IDs. Hard to shard.
    *   **Ticket Server**: You can use a dedicated DB just for IDs (Flickr did this), but it's still a bottleneck.

#### B. UUID (Universally Unique Identifier)
*   **Mechanism**: 128-bit random string (e.g., `123e4567-e89b-12d3-a456-426614174000`).
*   **Pros**: Zero coordination. Just generate it locally.
*   **Cons**:
    *   **Huge**: 128 bits is heavy on indexes.
    *   **Non-Sortable**: Random UUIDs fragment DB indexes (B-Tree splits), killing insert performance.

#### C. Twitter Snowflake (The Winner)
*   **Mechanism**: A 64-bit integer composed of:
    *   **Sign bit**: 1 bit (Unused).
    *   **Timestamp**: 41 bits (Milliseconds since epoch).
    *   **Machine ID**: 10 bits (Allows 1024 nodes).
    *   **Sequence**: 12 bits (Allows 4096 IDs per ms per node).
*   **Pros**: Sortable by time, Numerical (64-bit fits in `long`), Distributed (Each node generates its own).

---

## 💻 Code Simulation: Snowflake Generator

A Python implementation of the Snowflake algorithm.

```python
import time

class SnowflakeGenerator:
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1

        # Configuration
        self.epoch = 1609459200000 # Custom Epoch (e.g., 2021-01-01)
        self.machine_bits = 10
        self.sequence_bits = 12

        # Shift amounts
        self.machine_shift = self.sequence_bits
        self.timestamp_shift = self.sequence_bits + self.machine_bits

    def _current_timestamp(self):
        return int(time.time() * 1000)

    def next_id(self):
        timestamp = self._current_timestamp()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards!")

        if timestamp == self.last_timestamp:
            # Same millisecond: increment sequence
            self.sequence = (self.sequence + 1) & 4095 # 4095 = 2^12 - 1
            if self.sequence == 0:
                # Exhausted sequence, wait for next millisecond
                while timestamp <= self.last_timestamp:
                    timestamp = self._current_timestamp()
        else:
            # New millisecond: reset sequence
            self.sequence = 0

        self.last_timestamp = timestamp

        # Bitwise OR to combine parts
        id = ((timestamp - self.epoch) << self.timestamp_shift) | \
             (self.machine_id << self.machine_shift) | \
             self.sequence
        return id

if __name__ == "__main__":
    # Simulate Node 1
    gen = SnowflakeGenerator(machine_id=1)

    print("Generating 5 IDs...")
    for _ in range(5):
        print(gen.next_id())
```

**Output:**
```
Generating 5 IDs...
482910284910284800
482910284910284801
482910284910284802
482910284910284803
482910284910284804
```
*Note: They increase sequentially and look similar because they were generated in the same millisecond.*

---

## ⚠️ The Trap: "I'll use UUIDv4 for Primary Keys"
*   **Trap**: Using random UUIDs in MySQL/Postgres.
*   **Why**: B-Trees love sequential data. Inserting random data causes "Page Splitting" and fragmentation. The DB has to constantly rebalance the tree.
*   **The Fix**: Use **ULID** (Sortable UUID) or **Snowflake**. If you must use UUID, use UUIDv7 (Time-ordered).

---

## ⚡ Flashcards

1.  **Why 41 bits for timestamp?**
    *   $2^{41}$ milliseconds gives us ~69 years of IDs with a custom epoch.
2.  **What happens if the clock moves backwards (NTP skew)?**
    *   Snowflake fails. The system must refuse to generate IDs until the clock catches up, or throw an error.
3.  **How many IDs can Snowflake generate per second?**
    *   Per machine: 1000 ms * 4096 sequence = ~4 Million IDs/sec.
