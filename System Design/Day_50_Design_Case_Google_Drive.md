# Day 50: Design Google Drive (Dropbox)

## 🎯 Goal
Design a file hosting service with synchronization capabilities.
**Focus**: File Chunking, Deduplication, and Consistency (Sync).

---

## 🗣️ Requirements

### Functional
1.  **Upload/Download**: Support huge files.
2.  **Sync**: If I edit a file on PC, it updates on Phone.
3.  **Versioning**: Keep history of changes.
4.  **Sharing**: Share folders with read/write access.

### Non-Functional
1.  **Reliability**: Never lose data (11 nines durability).
2.  **Bandwidth Efficiency**: Don't re-upload the whole 1GB file if I change 1 byte.
3.  **ACID**: Metadata operations (move/rename) must be atomic.

---

## 📐 Capacity Estimation
*   **Users**: 100 Million.
*   **Storage**: 10GB/user -> 1 Exabyte total.
*   **QPS**: Sync traffic is bursty.

---

## 🧠 Core Design Decisions

### 1. Block-Level Deduplication
*   **Problem**: User A uploads "Batman.mkv" (2GB). User B uploads same file.
*   **Solution**: Hash the file. If hash exists, just add a pointer.
*   **Granularity**:
    *   **File-Level**: Good, but if I change 1 byte, I re-upload 2GB.
    *   **Block-Level**: Split file into 4MB blocks. Hash each block. Only upload changed blocks. **(Winner)**.

### 2. Synchronization Strategy
*   Client runs a **Watcher Service**.
*   When file changes, split into blocks -> calc hashes -> send list of hashes to server.
*   Server says: "I have Block A and B, but I need Block C".
*   Client uploads only Block C.

### 3. Metadata vs Block Storage
*   **Metadata DB**: Stores file hierarchy, permissions, versions. Needs ACID (Relational DB / NewSQL).
*   **Block Storage**: Stores the actual raw bytes (S3/Glacier). Immutable.

---

## 🏗️ System Architecture

1.  **Client Application**:
    *   **Watcher**: Listens to OS file events.
    *   **Chunker**: Splits files.
    *   **Indexer**: Local DB to track state.
2.  **Block Server**: Handles uploading raw blocks to S3.
3.  **Metadata Server**: Handles `rename`, `move`, `commit_version`.
4.  **Notification Service**: Long Polling / WebSocket. Tells other devices "File X changed".

### The Upload Flow
1.  Client changes `Report.docx`.
2.  Chunker splits it into 3 blocks (h1, h2, h3).
3.  Client asks Metadata Server: "I want to commit `Report.docx` with blocks [h1, h2, h3]".
4.  Server checks: "I have h1, h2. I miss h3".
5.  Client uploads h3 to Block Server.
6.  Block Server confirms "Stored h3".
7.  Client tells Metadata Server "Commit Done".
8.  Metadata Server updates DB and notifies other devices.

---

## 💻 Code Simulation: Differential Sync (Deduplication)

Simulating how splitting files into chunks saves bandwidth.

```python
import hashlib

class FileChunker:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.storage = {} # Hash -> Content (Simulating Block Storage)

    def upload_file(self, filename, content):
        print(f"📂 Processing: {filename} ({len(content)} bytes)")
        chunks = []
        saved_bytes = 0

        # Split content
        for i in range(0, len(content), self.chunk_size):
            chunk_data = content[i : i + self.chunk_size]
            chunk_hash = hashlib.sha256(chunk_data.encode()).hexdigest()

            # Deduplication Check
            if chunk_hash in self.storage:
                print(f"   ♻️  Found Duplicate Chunk: {chunk_hash[:8]}... (Saved Space!)")
                saved_bytes += len(chunk_data)
            else:
                self.storage[chunk_hash] = chunk_data
                print(f"   💾 Stored New Chunk: {chunk_hash[:8]}...")

            chunks.append(chunk_hash)

        print(f"✅ Upload Complete. Saved {saved_bytes} bytes via deduplication.\n")
        return chunks

if __name__ == "__main__":
    system = FileChunker(chunk_size=10) # Small chunk size for demo

    # File 1: "Hello World"
    file1 = "Hello World This is Data"
    meta1 = system.upload_file("file1.txt", file1)

    # File 2: Slightly different
    file2 = "Hello World This is Date" # Changed 'a' to 'e'
    meta2 = system.upload_file("file2.txt", file2)

    # Notice: First few chunks should be duplicates
```

---

## 🧠 Interview Nuances

### 1. How to handle Conflicts?
*   User A edits File X offline. User B edits File X online. User A comes online.
*   **Last Write Wins**: Simple, but data loss.
*   **Conflict File**: Create `File X (Conflicted Copy)`. Let user merge manually. (Standard approach).

### 2. Strong Consistency?
*   Metadata must be strongly consistent. You can't see a file "move" before it's "moved". Use SQL or CockroachDB.

### 3. Trash / Recovery?
*   Soft Delete. Mark `is_deleted = true`. Delete permanently after 30 days (Garbage Collection).

---

## ⚡ Flashcards
1.  **Block-Level vs Byte-Level Sync?**
    *   **Block-Level**: Chunks of 4MB. Good balance.
    *   **Byte-Level (Rsync)**: Rolling hash. Extremely efficient but computationally expensive (CPU heavy).
2.  **What is a Rolling Hash?**
    *   A hash function where input moves as a window. Useful for finding changed parts without fixed block boundaries.
3.  **Why separate Metadata and Block Storage?**
    *   Metadata (small, ACID needed) scales differently from Block Storage (Huge, Immutable). Separating them allows independent scaling.
