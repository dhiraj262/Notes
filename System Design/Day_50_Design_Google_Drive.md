# Day 50: Design Google Drive / Dropbox

## 🎯 Goal
Design a file storage and synchronization service.
**Focus**: File Chunking, Block Storage, Delta Sync (Rsync-like), and Consistency.

---

## 🗣️ Requirements

### Functional
1.  **Upload/Download**: Support huge files (GBs).
2.  **Sync**: Automatic sync across multiple devices.
3.  **Versioning**: Restore previous versions.
4.  **Sharing**: Share files via link.

### Non-Functional
1.  **Reliability**: 99.999999999% (11 nines) durability.
2.  **Bandwidth Efficiency**: Don't re-upload the whole file if only 1 byte changed.
3.  **ACID**: Metadata updates must be atomic.

---

## 📐 Capacity Estimation
*   **Users**: 100M DAU.
*   **Storage**: 10GB / user -> 1 Exabyte total. (Need Cold Storage).
*   **QPS**: Sync traffic is bursty.

---

## 🧠 Core Design Decisions

### 1. File Chunking & Deduplication
*   **Naive**: Store whole file `resume.doc`.
*   **Optimized**: Split file into 4MB chunks. Hash each chunk (SHA-256).
    *   If `Chunk_A` exists, don't upload it again.
    *   Saves massive storage and bandwidth.

### 2. Differential Sync (Delta Sync)
*   If I change 1 word in a 1GB file, only the changed chunk is uploaded.
*   **Rsync Algorithm**: Rolling hash to detect changes.

### 3. Separation of Metadata and Data
*   **Metadata DB (SQL)**: Stores `File_Name`, `Folder_Structure`, `List_of_Chunks`.
*   **Block Store (S3)**: Stores the actual raw chunks (Immutable).

---

## 🏗️ System Architecture

1.  **Client (Watcher)**:
    *   Monitors local folder.
    *   Chunks files. Calculates Hashes.
    *   Asks Server: "Do you have Hash X?"
    *   Uploads only missing hashes.
2.  **Block Server**:
    *   Receives raw chunks -> S3.
3.  **Metadata Service**:
    *   Updates SQL: `File_v2` points to `[Hash1, Hash2, Hash3_New]`.
4.  **Notification Service**:
    *   Long Polling / WebSocket.
    *   Tells other devices: "File Updated, download new chunks".

---

## 💻 Code Simulation: Chunking & Dedup

Simulating how a file is broken into blocks and deduplicated.

```python
import hashlib

class CloudStorage:
    def __init__(self):
        self.block_storage = {} # Hash -> Data
        self.file_metadata = {} # Filename -> [Hash1, Hash2, ...]

    def upload_file(self, filename, content):
        print(f"📂 Uploading: {filename}")
        chunks = self._chunk_file(content)
        block_hashes = []

        for chunk in chunks:
            h = self._hash(chunk)
            if h not in self.block_storage:
                print(f"   💾 New Block {h[:6]}... stored.")
                self.block_storage[h] = chunk
            else:
                print(f"   ♻️ Dedup: Block {h[:6]}... already exists.")
            block_hashes.append(h)

        self.file_metadata[filename] = block_hashes
        print("✅ Upload Complete.\n")

    def download_file(self, filename):
        print(f"📥 Downloading: {filename}")
        hashes = self.file_metadata.get(filename, [])
        content = ""
        for h in hashes:
            content += self.block_storage[h]
        print(f"   Content: {content}\n")

    def _chunk_file(self, content, chunk_size=4):
        return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

    def _hash(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

if __name__ == "__main__":
    drive = CloudStorage()

    # User A uploads a file
    drive.upload_file("Resume.txt", "Hello World This is Data")

    # User B uploads a slightly modified version (Differential Sync simulation)
    drive.upload_file("Resume_v2.txt", "Hello World This is Date")

    drive.download_file("Resume_v2.txt")
```

**Output:**
```
📂 Uploading: Resume.txt
   💾 New Block ... stored.
   💾 New Block ... stored.
✅ Upload Complete.

📂 Uploading: Resume_v2.txt
   ♻️ Dedup: Block ... already exists.
   💾 New Block ... stored. (Only the last chunk changed)
✅ Upload Complete.
```

---

## 🧠 Interview Nuances

### 1. Conflict Resolution?
*   Two users edit `resume.doc` offline. Both come online.
*   **Strategy**: Create `resume (User A's conflicted copy).doc`.
*   **Better**: Use Operational Transformation (OT) or CRDTs for real-time collab (Google Docs), but for Drive, "Last Write Wins" or "Conflict Copy" is standard.

### 2. Namespace / Folder Structure?
*   It's a graph (DAG) or Tree.
*   Store as `Parent_ID` in SQL table. `Files (ID, Name, ParentID, IsFolder)`.

### 3. Trash / Recycle Bin?
*   Don't delete chunks immediately. Mark metadata as `is_deleted=True`.
*   Run Garbage Collection (GC) job every 30 days to remove orphaned chunks (chunks not referenced by any file).

---

## ⚡ Flashcards
1.  **What is Block-Level Deduplication?**
    *   Saving only one copy of a data block (chunk) even if it appears in multiple files or versions.
2.  **Why use Strong Consistency for Metadata?**
    *   If I move a file, I expect to see it moved immediately on my other device. (ACID DB required).
3.  **What is a Cold Storage?**
    *   Cheap, slow-access storage (AWS Glacier) for data not accessed frequently (Archives).
