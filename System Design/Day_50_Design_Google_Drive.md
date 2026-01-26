# Day 50: Design Google Drive

## 🎯 Goal
Design a file storage and synchronization service like Google Drive or Dropbox.
**Focus**: File Chunking, Block Storage, Metadata management, and Delta Sync.

---

## 🗣️ Requirements

### Functional
1.  **File Upload/Download**: Drag and drop files.
2.  **File Sync**: Changes on one device sync to others automatically.
3.  **Revision History**: Restore previous versions of a file.
4.  **Sharing**: Share files with specific users via link.

### Non-Functional
1.  **Reliability**: Never lose a file (99.999999999% Durability).
2.  **Consistency**: Syncing should be eventually consistent across devices.
3.  **Efficiency**: Don't re-upload the whole file if only one byte changed.

---

## 📐 Capacity Estimation
*   **Users**: 100 Million DAU.
*   **Storage**: 10GB free per user. 100M * 10GB = 1 Exabyte (Huge).
*   **Traffic**: Read Heavy, but "Sync" traffic is "Write" heavy (metadata updates).

---

## 🧠 Core Design Decisions

### 1. File Chunking
*   **Problem**: Uploading a 2GB file as one blob is bad. If network fails at 99%, we retry 2GB.
*   **Solution**: Split files into **Blocks** (e.g., 4MB chunks).
*   Upload blocks in parallel. Retry only failed blocks.

### 2. Deduplication (Data Compression)
*   **Problem**: 1000 users upload the exact same "Ubuntu.iso". Storing 1000 copies is wasteful.
*   **Solution**: Calculate hash (SHA-256) of each block.
*   If Hash `H1` exists in Block Storage, don't upload. Just link User B's file metadata to `H1`.

### 3. Delta Sync (rsync algorithm)
*   If I change one word in a large Word Doc, only the modified block is uploaded.
*   Client calculates hashes of local blocks, compares with server, uploads difference.

---

## 🏗️ System Architecture

1.  **Client**:
    *   **Watcher**: Detects local file changes.
    *   **Chunker**: Splits file into blocks.
2.  **Block Server**:
    *   Uploads raw blocks to **S3** (Cloud Storage).
    *   Checks duplication using hashes.
3.  **Metadata Database** (SQL):
    *   Stores file hierarchy (Folders, Names).
    *   Maps `File_ID` -> `[Block_ID_1, Block_ID_2, ...]`.
    *   **Cold vs Hot**: Recent metadata in SQL, Archived metadata in NoSQL.
4.  **Notification Service**:
    *   Uses Long Polling / WebSockets to tell other devices "File X changed, download it."

---

## 💻 Code Simulation: File Chunking

Simulating splitting a file and generating block hashes.

```python
import hashlib

class DriveClient:
    def __init__(self, block_size=1024): # 1KB blocks for demo
        self.block_size = block_size

    def upload_file(self, filename, content):
        print(f"📂 Processing '{filename}' ({len(content)} bytes)...")

        blocks = []
        for i in range(0, len(content), self.block_size):
            chunk = content[i : i + self.block_size]
            chunk_hash = hashlib.sha256(chunk.encode()).hexdigest()
            blocks.append((chunk_hash, chunk))

        self.send_metadata(filename, [b[0] for b in blocks])
        self.upload_blocks(blocks)

    def send_metadata(self, filename, hashes):
        print(f"   📝 Metadata Update: {filename} maps to blocks {hashes}")

    def upload_blocks(self, blocks):
        for h, data in blocks:
            # Simulate checking if block exists
            if self.check_dedup(h):
                print(f"   ⏩ Block {h[:8]}... exists. Skipping upload.")
            else:
                print(f"   ⬆️ Uploading Block {h[:8]}...")

    def check_dedup(self, hash_val):
        # Mock: Let's say any hash starting with 'a' exists
        return hash_val.startswith('a')

if __name__ == "__main__":
    drive = DriveClient(block_size=10) # Small blocks

    # "Hello World" repeated
    file_content = "Hello World " * 5
    drive.upload_file("notes.txt", file_content)
```

**Output:**
```
📂 Processing 'notes.txt' (60 bytes)...
   📝 Metadata Update: notes.txt maps to blocks ['a591...', 'e3b0...', ...]
   ⏩ Block a591... exists. Skipping upload.
   ⬆️ Uploading Block e3b0...
   ...
```

---

## 🧠 Interview Nuances

### 1. ACID Requirements?
*   Metadata (File structure) needs ACID. If I move a folder, it must happen atomically. Use **Relational DB** (Postgres/MySQL) for Metadata.
*   File Content (Blocks) is in S3 (Immutable).

### 2. Offline Editing?
*   Client queues changes locally in a SQLite DB.
*   When online, pushes changes.
*   **Conflict Resolution**: If two users edit same file, create "Conflicted Copy" (let user resolve) or "Last Write Wins" (bad for docs).

### 3. Security?
*   Encryption at Rest (S3 SSE).
*   Encryption in Transit (TLS).
*   Client-side encryption (Zero-knowledge) is a differentiator but breaks "Search" features.

---

## ⚡ Flashcards
1.  **What is Delta Sync?**
    *   A strategy to reduce bandwidth by only transferring the parts of a file that have changed, rather than the entire file.
2.  **Why separate Metadata from Block Storage?**
    *   Metadata (small, relational) needs fast updates and queries. Block data (large, immutable) needs cheap, durable storage like S3. Scaling them independently is key.
3.  **What is Block-Level Deduplication?**
    *   Saving storage space by storing only one copy of a data block (identified by its hash), even if multiple users upload files containing that same block.
