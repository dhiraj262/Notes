# 🛑 Interview Post-Mortem: "I Bombed Database Indexing"

> **Context**: Everyone knows "Add an Index". But Senior engineers must know *which* index (B-Tree vs LSM) and the cost of indexing (Write Amplification).

---

## 1. The Trap: "Index Everything" & "B-Tree for All"

**The Scenario**: You are designing a high-throughput IoT ingestion system (writes >> reads).
The interviewer asks: *"How do we store these sensor readings?"*
You answer: *"Postgres with a B-Tree index on timestamp."*

**The Kill Shot**: *"B-Trees require random I/O to rebalance the tree on inserts. If we have 1 million writes/sec, the disk head will thrash. Your database will lock up. How do we optimize for **Writes**?"*

**The Failure**: Treating all databases as B-Tree (Read-Optimized) engines. Ignoring **Log-Structured Merge (LSM) Trees**.

---

## 2. The Solution: LSM Trees (Cassandra, RocksDB)

**Concept**: Instead of updating a big tree on disk (Random I/O), we append data to an in-memory buffer (MemTable). When full, we flush it to disk as a sorted file (SSTable).

**Why it wins for Writes**:
*   **Sequential I/O**: Flushing to disk is a linear write. HDDs/SSDs love this.
*   **No Locking**: We don't need to lock a B-Tree page to split it.

**Trade-off**: Reads are slower. You have to check the MemTable and *all* SSTables on disk. (Fix: Bloom Filters).

---

## 3. The Implementation: Python LSM Simulation

**The logic**:
1.  **Write**: Add to `MemTable` (Dict).
2.  **Flush**: When `MemTable` > limit, write to `SSTable` (File).
3.  **Read**: Check `MemTable` -> Check `SSTables` (Newest to Oldest).

```python
import os
import json
import time

class LSMTree:
    def __init__(self, memtable_limit=3):
        self.memtable = {}
        self.memtable_limit = memtable_limit
        self.sstables = [] # List of filenames
        self.wal_log = "wal.log"

    def put(self, key, value):
        # 1. Write Ahead Log (WAL) for durability
        with open(self.wal_log, "a") as f:
            f.write(f"{key}:{value}\n")

        # 2. Write to MemTable
        self.memtable[key] = value
        print(f"📝 Write MemTable: {key}={value}")

        # 3. Check Flush Condition
        if len(self.memtable) >= self.memtable_limit:
            self._flush()

    def _flush(self):
        # Create SSTable (Sorted String Table)
        filename = f"sstable_{int(time.time() * 1000)}.json"

        # Sort keys for efficient search (conceptually)
        sorted_data = dict(sorted(self.memtable.items()))

        with open(filename, "w") as f:
            json.dump(sorted_data, f)

        self.sstables.insert(0, filename) # Newest first
        print(f"💾 FLUSH: MemTable -> {filename}")

        # Reset MemTable
        self.memtable = {}
        # Clear WAL (Simplified)
        open(self.wal_log, 'w').close()

    def get(self, key):
        # 1. Check MemTable
        if key in self.memtable:
            print(f"🔍 Found in MemTable: {key}")
            return self.memtable[key]

        # 2. Check SSTables (Newest -> Oldest)
        for filename in self.sstables:
            if not os.path.exists(filename): continue

            # optimization: Bloom Filter would go here

            with open(filename, "r") as f:
                data = json.load(f)
                if key in data:
                    print(f"🔍 Found in SSTable ({filename}): {key}")
                    return data[key]

        print(f"❌ Key not found: {key}")
        return None

    def compaction(self):
        """Merge all SSTables into one (Simplified)"""
        print("🚜 Starting Compaction...")
        merged_data = {}
        # Read oldest to newest to let newer keys overwrite older ones
        for filename in reversed(self.sstables):
            with open(filename, "r") as f:
                data = json.load(f)
                merged_data.update(data)

        new_filename = f"sstable_compacted_{int(time.time())}.json"
        with open(new_filename, "w") as f:
            json.dump(merged_data, f)

        # Cleanup
        for f in self.sstables:
            os.remove(f)
        self.sstables = [new_filename]
        print(f"✅ Compaction Complete: {new_filename}")

# --- Simulation ---
db = LSMTree(memtable_limit=2)

db.put("user_1", "Alice")
db.put("user_2", "Bob") # Triggers Flush

db.put("user_1", "Alice_Updated") # Update
db.put("user_3", "Charlie") # Triggers Flush

print("\n--- Reads ---")
print(f"Get user_1: {db.get('user_1')}") # Should be Alice_Updated
print(f"Get user_2: {db.get('user_2')}")

print("\n--- Compaction ---")
db.compaction()
print(f"SSTables: {db.sstables}")
```

---

## 4. Production Realities (The "Senior" Section)

### A. Bloom Filters
*   **Problem**: To find a key, we have to check *every* SSTable on disk. This is slow (Read Amplification).
*   **Fix**: A **Bloom Filter** is a memory-efficient probabilistic structure that answers "Definitely No" or "Maybe Yes". We check the Bloom Filter first. If it says "No", we skip opening the file.

### B. Compaction Strategies
*   **Leveled Compaction (RocksDB)**: Merges small SSTables into larger "Levels". Optimizes for Reads.
*   **Size-Tiered Compaction (Cassandra)**: Waits for huge buckets to merge. Optimizes for Writes.

### C. Leftmost Prefix Rule (B-Trees)
*   **Trap**: Index is `(Region, Date)`. Query is `WHERE Date > '2023'`.
*   **Result**: Full Table Scan. The index is sorted by Region first. You cannot skip to Date without picking a Region.

---

## 🧠 Flashcards

1.  **Q: Why is LSM better for Writes than B-Tree?**
    *   *A: LSM converts random writes into Sequential I/O (Append-only). B-Trees require random disk seeks to rebalance nodes.*
2.  **Q: What is the downside of LSM?**
    *   *A: Slower Reads (Need to check MemTable + multiple SSTables). Solved with Bloom Filters and Compaction.*
3.  **Q: What is Write Amplification?**
    *   *A: One logical write causes multiple physical writes (WAL + MemTable Flush + Compaction cycles).*
4.  **Q: Does `SELECT * FROM table WHERE col LIKE '%term'` use an index?**
    *   *A: No. A leading wildcard (`%`) prevents using the B-Tree sort order.*
