# 🪵 Deep Dive: Segmented Log

> **Category**: Durability & Storage
> **Core Concept**: Splitting a conceptually infinite log into smaller, manageable files (segments) to allow for easier lookup, rotation, and deletion (compaction).

---

## 1. The Concept

A single **Write-Ahead Log (WAL)** cannot grow forever. It would consume all disk space and make startup recovery impossibly slow.
**Segmented Logs** break the WAL into fixed-size files (e.g., 1GB each).

### Anatomy
1.  **Active Segment**: The current file being written to. (Open for writes).
2.  **Sealed Segments**: Older files that are full and Read-Only.
3.  **Offset Index**: A Map `{Offset -> Segment File}`. If you need Offset `10050`, and Segment 1 ends at `10000`, look in Segment 2.

---

## 2. Interview Post-Mortem: "The Infinite File"

### 🛑 The Trap
**Scenario**: Building a Message Queue (like Kafka).
**Candidate**: *"I'll append all messages to a file `queue.log`. To read message #1000, I'll seek to that line."*

**The Kill Shot**: *"What happens when `queue.log` is 10TB? How do you delete old messages? You can't delete the beginning of a file easily without rewriting the whole thing."*

### ✅ The Solution
Use **Segments**.
*   `0000.log`: Messages 0-999.
*   `1000.log`: Messages 1000-1999.
*   *Retention Policy*: To delete messages older than 1 week, simply `rm 0000.log`. No file rewriting needed. $O(1)$ deletion.

---

## 3. Implementation (Python Simulation)

```python
import os

class LogSegment:
    def __init__(self, start_offset, capacity=5):
        self.start_offset = start_offset
        self.capacity = capacity
        self.current_offset = start_offset
        self.data = [] # Simulating Disk File
        self.is_sealed = False

    def append(self, message):
        if self.is_sealed:
            raise Exception("Segment Sealed")

        self.data.append(message)
        self.current_offset += 1

        if len(self.data) >= self.capacity:
            self.seal()
            return False # Full
        return True # Accepted

    def seal(self):
        self.is_sealed = True
        print(f"🔒 Segment {self.start_offset} Sealed. Range: [{self.start_offset}, {self.current_offset-1}]")

class SegmentedLog:
    def __init__(self):
        self.segments = []
        self.active_segment = LogSegment(start_offset=0)
        self.segments.append(self.active_segment)

    def write(self, message):
        success = self.active_segment.append(message)
        if not success:
            # Rotate
            new_offset = self.active_segment.current_offset
            self.active_segment = LogSegment(start_offset=new_offset)
            self.segments.append(self.active_segment)
            # Retry write in new segment
            self.active_segment.append(message)

        print(f"📝 Wrote '{message}' to Segment {self.active_segment.start_offset}")

    def read(self, offset):
        # Find correct segment
        for seg in self.segments:
            if seg.start_offset <= offset < seg.current_offset:
                local_index = offset - seg.start_offset
                return seg.data[local_index]
        return None

# --- Test ---
log = SegmentedLog()
for i in range(12):
    log.write(f"msg_{i}")

print(f"\nRead Offset 7: {log.read(7)}")
```

---

## 4. Production Realities

### A. Compaction
*   In systems like **Kafka** (Key-Value mode) or **Cassandra**, we don't just delete old segments. We **Compact** them.
*   If Segment 1 has `A=10` and Segment 2 has `A=20`, we can keep only `A=20` and discard the old key from Segment 1 during a background merge.

### B. Indexing
*   Scanning segments is slow.
*   **Sparse Index**: Keep an in-memory map of `Offset -> File Position` for every 4KB of data. Allows fast `fseek`.

---

## ⚡ Flashcards
1.  **Q: Why use segments instead of one big file?**
    *   *A: Allows efficient deletions (dropping old files) and fast lookups (binary search on segment names).*
2.  **Q: What is "Log Rotation"?**
    *   *A: The process of closing the active segment and creating a new one based on size or time.*
3.  **Q: How does Kafka find a message by offset?**
    *   *A: It uses a binary search on the file names (e.g., `0.log`, `1000.log`) to find the segment, then an index to find the position.*
