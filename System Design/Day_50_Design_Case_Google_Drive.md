# Day 50: Design Case - Google Drive / Dropbox

## 🎯 Goal
Design a file storage and synchronization service.
**Scale**: 100 Million DAU. Storage heavy.

---

## 🗣️ Requirements

### Functional
1.  **File Upload/Download**: Drag and drop support.
2.  **Sync**: Sync files across multiple devices (Laptop, Phone, Tablet).
3.  **Versioning**: Restore previous versions of a file.
4.  **Sharing**: Share files with other users via email/link.

### Non-Functional
1.  **Reliability**: Data must NEVER be lost (11 nines durability).
2.  **Sync Speed**: Changes should reflect quickly.
3.  **Efficiency**: Don't re-upload the whole 1GB file if only 1 byte changed (Delta Sync).

---

## 📐 Capacity Estimation
*   **Users**: 100M DAU.
*   **Storage**:
    *   Avg user stores 10GB.
    *   Total = 100M * 10GB = 1 Exabyte (EB).
    *   Requires Cold Storage (Glacier) for old files to save cost.
*   **Bandwidth**: High upload traffic.

---

## 🧠 Core Design Decisions

### 1. Chunking & Block Storage
*   Uploading a 10GB file as a single blob is bad (resume failure, no dedup).
*   **Solution**: Split files into **Blocks** (e.g., 4MB chunks).
*   **Deduplication**: Calculate hash (SHA-256) of each block. If hash exists in DB, don't upload content. Just link it. saves ~40% space.

### 2. Metadata Database
*   Separation of **Metadata** (File Name, Folder Structure, Permissions) from **Data** (Content Blocks).
*   **Metadata DB**: SQL (MySQL/Postgres) because ACID is needed for file moves/renames.
*   **Block Store**: S3/HDFS.

### 3. Synchronization (Delta Sync)
*   User edits `Resume.docx`.
*   Client calculates hashes of new blocks.
*   Client sends ONLY the modified blocks to server.
*   Server updates Metadata to point to new blocks for the new version.

---

## 🏗️ System Architecture

1.  **Client Application**: Runs background daemon. Watches file system events.
2.  **Block Server**: Handles raw data upload/download to S3.
3.  **Metadata Server**: Handles logic (Create File, Move, Share). Updates DB.
4.  **Notification Service**:
    *   User A updates file.
    *   Server pushes notification to User A's other devices (and Shared User B).
    *   Devices pull the new metadata and download changed blocks.
5.  **Offline Support**: Queue changes locally. Sync when online.

---

## 💻 Code Simulation: Block Deduplication

Simulating how a file is split into blocks and how only changed blocks are uploaded.

```python
import hashlib

class BlockStorage:
    def __init__(self):
        self.blocks = {} # hash -> content

    def save_block(self, content):
        h = hashlib.sha256(content.encode()).hexdigest()
        if h in self.blocks:
            print(f"   ♻️ Block Deduplicated (Hash: {h[:8]}...)")
            return h, False # False = Not New

        self.blocks[h] = content
        print(f"   💾 Block Saved (Hash: {h[:8]}...)")
        return h, True

class DriveClient:
    def __init__(self, storage):
        self.storage = storage

    def upload_file(self, filename, content):
        print(f"\n⬆️ Uploading '{filename}'...")
        # Split into blocks (Fixed size for sim: 10 chars)
        block_size = 10
        metadata = []

        for i in range(0, len(content), block_size):
            chunk = content[i:i+block_size]
            block_hash, is_new = self.storage.save_block(chunk)
            metadata.append(block_hash)

        return metadata

if __name__ == "__main__":
    storage = BlockStorage()
    client = DriveClient(storage)

    # 1. Upload File A
    file_a = "Hello World This Is Data"
    meta_a = client.upload_file("FileA.txt", file_a)

    # 2. Upload File B (Minor change)
    # "Hello World" is same. "This Is " is same. "Beta" is different.
    file_b = "Hello World This Is Beta"
    meta_b = client.upload_file("FileB.txt", file_b)

    # 3. Verify Metadata
    print("\n--- Metadata Verification ---")
    print(f"FileA Blocks: {len(meta_a)}")
    print(f"FileB Blocks: {len(meta_b)}")
    print(f"Common Blocks: {len(set(meta_a).intersection(set(meta_b)))}")
```

**Output:**
```
⬆️ Uploading 'FileA.txt'...
   💾 Block Saved (Hash: 12fec4c6...)
   💾 Block Saved (Hash: 630b7ea0...)
   💾 Block Saved (Hash: cec3a9b8...)

⬆️ Uploading 'FileB.txt'...
   ♻️ Block Deduplicated (Hash: 12fec4c6...)
   ♻️ Block Deduplicated (Hash: 630b7ea0...)
   💾 Block Saved (Hash: 70339031...)

--- Metadata Verification ---
FileA Blocks: 3
FileB Blocks: 3
Common Blocks: 2
```

---

## 🧠 Interview Nuances

### 1. Conflict Resolution?
*   Two users edit the same file offline and come online.
*   **Strategy**: "Last Write Wins" (bad for docs) or **Create Conflicting Copy** (Dropbox style).
*   For collaborative editing (Google Docs), you need **Operational Transformation (OT)** or CRDTs, which is a different design than Drive.

### 2. Namespace / Directory Structure?
*   How to store `/A/B/C/file.txt` in SQL?
*   **Approach**: Adjacency List (`id`, `parent_id`, `name`).
*   Faster Reads: **Closure Table** or **Path Enumeration** if deep nesting is common.

### 3. Trash / Recycle Bin?
*   Don't delete immediately. Set `is_deleted = true`.
*   Run a cleanup job (Cron) every 30 days to permanently delete data from S3.

---

## ⚡ Flashcards
1.  **What is Delta Sync?**
    *   Synchronizing only the parts of a file that changed, rather than the whole file.
2.  **Why split files into blocks?**
    *   Enables parallel uploads, deduplication, and efficient delta sync.
3.  **Strong vs Eventual Consistency for Metadata?**
    *   Metadata (Folder structure) usually needs Strong Consistency (ACID) so users don't see "Ghost files".
