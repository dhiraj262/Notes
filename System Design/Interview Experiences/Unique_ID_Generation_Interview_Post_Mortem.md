# 🆔 System Design Deep Dive: Unique ID Generation

> **Context**: Strategies for generating unique, sortable IDs in distributed systems. Comparing Auto-Increment, UUID, and the Twitter Snowflake algorithm.

---

## 1. The Trap: "Auto-Increment or UUID"

**The Scenario**: You are designing a Distributed Message Queue (like Kafka) or an Instagram clone. The interviewer asks, *"How do we generate unique IDs for every message/post?"*

**The Amateur Answers**:
1.  **"Use Database Auto-Increment!"**:
    *   *The Kill Shot*: "We have 10 database write masters across 3 regions. How do you synchronize the counter? What if the master dies?"
    *   *Result*: Single Point of Failure (SPOF) and Write Bottleneck.
2.  **"Use UUID (v4)!"**:
    *   *The Kill Shot*: "Your primary key is a clustered index (B-Tree). UUIDs are random. Inserting random keys causes massive **Page Fragmentation** and random I/O."
    *   *Result*: Database write performance degrades significantly as table grows.

---

## 2. The Solution: Twitter Snowflake (64-bit Integers)

**Concept**: Generate a 64-bit integer that is composed of a Timestamp, a Machine ID, and a Sequence Number.

**Structure (Total 64 bits)**:
*   **1 bit**: Sign bit (Unused, always 0).
*   **41 bits**: Timestamp (Milliseconds since custom Epoch). Gives us ~69 years.
*   **10 bits**: Machine ID (5 bits Datacenter + 5 bits Worker). Supports 1024 nodes.
*   **12 bits**: Sequence Number. Supports 4096 IDs *per millisecond* per node.

**Why it wins**:
*   **Sortable**: Higher bits are time. ID A > ID B implies A was created after B.
*   **Distributed**: Each node generates IDs independently. No coordination needed.
*   **Compact**: 64-bit integer fits in a CPU register (unlike 128-bit String UUID).

---

## 3. The Implementation: Python Snowflake Generator

**The logic**: Bitwise shifts `<<` and OR `|` operations to pack the data.

```python
import time
import threading

class SnowflakeGenerator:
    def __init__(self, datacenter_id, worker_id, epoch=1609459200000):
        """
        :param datacenter_id: 0-31
        :param worker_id: 0-31
        :param epoch: Custom Epoch (e.g., 2021-01-01) in milliseconds
        """
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.epoch = epoch

        self.sequence = 0
        self.last_timestamp = -1

        # Bit allocations
        self.timestamp_bits = 41
        self.datacenter_bits = 5
        self.worker_bits = 5
        self.sequence_bits = 12

        # Max values (for validation)
        self.max_datacenter_id = (1 << self.datacenter_bits) - 1
        self.max_worker_id = (1 << self.worker_bits) - 1
        self.max_sequence = (1 << self.sequence_bits) - 1

        # Shifts
        self.worker_shift = self.sequence_bits
        self.datacenter_shift = self.sequence_bits + self.worker_bits
        self.timestamp_shift = self.sequence_bits + self.worker_bits + self.datacenter_bits

        self.lock = threading.Lock()

        if self.datacenter_id > self.max_datacenter_id or self.worker_id > self.max_worker_id:
            raise ValueError("ID out of range")

    def _current_timestamp(self):
        return int(time.time() * 1000)

    def _wait_for_next_millis(self, last_timestamp):
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def next_id(self):
        with self.lock:
            timestamp = self._current_timestamp()

            # 🕒 CLOCK ROLLBACK PROTECTION
            if timestamp < self.last_timestamp:
                raise Exception(f"Clock moved backwards! Refusing to generate id for {self.last_timestamp - timestamp}ms")

            # If same millisecond, increment sequence
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                # Sequence Exhausted (4096 ids in 1ms)? Wait for next ms
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                self.sequence = 0 # New millisecond, reset sequence

            self.last_timestamp = timestamp

            # 📦 PACK BITS
            new_id = ((timestamp - self.epoch) << self.timestamp_shift) | \
                     (self.datacenter_id << self.datacenter_shift) | \
                     (self.worker_id << self.worker_shift) | \
                     self.sequence

            return new_id

# Usage
generator = SnowflakeGenerator(datacenter_id=1, worker_id=1)
print(f"Generated ID: {generator.next_id()}")
```

---

## 4. Production Realities (The "Senior" Section)

### A. Clock Synchronization (NTP)
*   **Problem**: Snowflake relies on wall-clock time. If a server's clock drifts, ID order is skewed.
*   **Fix**: Use NTP (Network Time Protocol) on all servers. But NTP isn't perfect.

### B. Clock Rollback (The Nightmare)
*   **Scenario**: NTP corrects a drifting clock by moving it *backwards* 500ms.
*   **Risk**: You might generate a duplicate ID that was issued 500ms ago.
*   **Fix**:
    1.  **Wait**: If rollback is small (< 5ms), sleep and wait it out.
    2.  **Crash**: If rollback is large, kill the process. It's better to be down than to corrupt data with duplicates.

### C. Node ID Management
*   **Problem**: How do you ensure Worker ID #1 is not assigned to two active pods at the same time?
*   **Fix**: use **ZooKeeper** or **Etcd** to assign Worker IDs to pods at startup.

---

## 🧠 Flashcards

1.  **Q: Why is UUID v4 bad for Primary Keys in MySQL/Postgres?**
    *   *A: It is random and non-sequential. Inserts into a B-Tree index require re-balancing and random I/O (Page Splitting).*
2.  **Q: How many IDs can a Snowflake node generate per millisecond?**
    *   *A: 4096 (due to the 12-bit sequence number).*
3.  **Q: What happens if the clock moves backwards?**
    *   *A: The generator must pause or throw an exception to prevent generating a duplicate ID.*
4.  **Q: How long until the 41-bit timestamp overflows?**
    *   *A: Approx 69 years from the custom epoch.*
5.  **Q: Why do we need a custom Epoch?**
    *   *A: To maximize the lifespan of the 41-bit timestamp. If we used the standard Unix Epoch (1970), we would have wasted 50+ years of value.*
