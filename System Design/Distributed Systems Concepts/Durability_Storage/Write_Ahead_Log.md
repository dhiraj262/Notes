# 📝 Deep Dive: Write-Ahead Log (WAL)

> **Category**: Durability & Storage
> **Core Concept**: An append-only file where every state change is recorded *before* it is applied to the database pages/memory.
> **Mantra**: "Log first, Apply second."

---

## 1. The Concept

Databases store data in memory (RAM) for speed. If power fails, RAM is erased.
To guarantee **Durability** (The 'D' in ACID), the DB must write the change to a persistent disk.
Writing random pages to disk (B-Tree nodes) is slow (Random I/O).
Writing to the **WAL** is fast (Sequential I/O).

### The Flow
1.  **Client**: `UPDATE users SET age=30 WHERE id=1`
2.  **DB (RAM)**: Lock row. Create Log Entry.
3.  **DB (Disk)**: Append Log Entry to `wal.log`. **fsync**.
4.  **DB (RAM)**: Modify the in-memory Page.
5.  **Client**: Receive "Success".
6.  **Background**: Periodically flush the modified RAM page to the actual data file (Checkpointing).

---

## 2. Crash Recovery (ARIES Algorithm)

If the DB crashes:
1.  **Analysis Phase**: Read WAL from the last Checkpoint to find "Dirty Pages".
2.  **Redo Phase**: Replay *all* operations in the WAL to bring the DB to the state at the moment of crash (even uncommitted ones).
3.  **Undo Phase**: Reverse (Rollback) any transactions that were active (uncommitted) at the time of crash.

---

## 3. Implementation (Python Logger)

A simple simulation of a WAL-based storage engine.

```python
import os

class WALEngine:
    def __init__(self):
        self.memory = {} # RAM state
        self.log_file = "simulation.wal"
        # Recover on startup
        self._recover()

    def _recover(self):
        if not os.path.exists(self.log_file):
            return

        print("🚑 Recovering from WAL...")
        with open(self.log_file, "r") as f:
            for line in f:
                # Replay Log
                key, value = line.strip().split("=")
                self.memory[key] = value
                print(f"   Redo: {key} -> {value}")

    def write(self, key, value):
        # 1. Write Ahead to Disk
        with open(self.log_file, "a") as f:
            f.write(f"{key}={value}\n")
            f.flush()
            os.fsync(f.fileno()) # Force write to physical disk

        # 2. Update Memory
        self.memory[key] = value
        print(f"✅ Written {key}={value}")

    def read(self, key):
        return self.memory.get(key)

    def crash(self):
        print("💥 CRASH! Memory wiped.")
        self.memory = {}

# --- Simulation ---
# 1. Start Engine
db = WALEngine()
db.write("A", "100")
db.write("B", "200")

# 2. Simulate Crash
db.crash()
print(f"Read A after crash: {db.read('A')}") # None

# 3. Restart (Recovery)
print("\n--- Restarting ---")
db_restarted = WALEngine()
print(f"Read A after recovery: {db_restarted.read('A')}") # 100
```

---

## 4. Production Realities

### A. Segmented Logs
*   WAL grows infinitely. We split it into **Segments** (e.g., 1GB files).
*   Once a segment is fully flushed to the main Data files (Checkpointed), that segment can be deleted or archived.

### B. Sync vs Async Commit
*   **fsync is expensive**.
*   **Group Commit**: Wait for 10 transactions, then write them all to WAL in one `fsync`. Improves throughput, slightly increases latency.
*   **Async Commit** (Postgres `synchronous_commit=off`): Don't wait for WAL. Risk of losing last few milliseconds of data, but massive speedup.

---

## ⚡ Flashcards
1.  **Q: Why not just write to the data file directly?**
    *   *A: Data files (B-Trees) require random I/O which is slow. WAL is Append-Only (Sequential I/O), which is 10-100x faster.*
2.  **Q: What is a Checkpoint?**
    *   *A: The process of flushing modified pages ("Dirty Pages") from RAM to the actual Data Files, allowing us to truncate the WAL.*
3.  **Q: Is WAL used in NoSQL?**
    *   *A: Yes. Cassandra calls it CommitLog. HBase calls it WAL. It's universal for durability.*
