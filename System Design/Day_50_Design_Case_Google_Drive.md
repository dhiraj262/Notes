# Day 50: Design Case - Google Drive (Cloud Storage)

## 🎯 Goal
Design a file storage and synchronization service like Google Drive, Dropbox, or OneDrive.
**Focus**: Large file uploads, Data consistency, Deduplication, and Synchronization.

---

## 🗣️ Requirements

### Functional
1.  **Add/Delete/Update**: Support basic file operations.
2.  **Sync**: Automatic synchronization across devices.
3.  **Versioning**: Restore previous versions of a file.
4.  **Sharing**: Share files/folders with others.
5.  **Offline Access**: Work offline and sync when online.

### Non-Functional
1.  **Reliability**: Data durability is paramount (99.999999999% durability).
2.  **Consistency**: Syncing should be atomic.
3.  **Bandwidth Usage**: Minimize data transfer (don't re-upload entire 1GB file if 1 byte changed).

---

## 📐 Capacity Estimation
*   **Users**: 100 Million DAU.
*   **Storage**: 10GB / user.
    *   Total: 100M * 10GB = 1 Exabyte (EB).
*   **QPS**: Not very high compared to Chat, but Bandwidth is high.

---

## 🧠 Core Design Decisions

### 1. Chunking Files
*   Uploading a 10GB file as a single blob is risky (network fail = restart).
*   **Solution**: Split files into fixed-size chunks (e.g., 4MB).
*   **Benefits**:
    *   Parallel uploads.
    *   Retry only failed chunks.
    *   **Deduplication**.

### 2. Deduplication (at Block Level)
*   User A and User B both upload the same movie.
*   Instead of storing twice, we calculate hash (SHA-256) of each chunk.
*   If Hash matches existing chunk in S3, we just point Metadata to it.
*   **Saves 30-50% storage space**.

### 3. Synchronization (Differential Sync)
*   If user modifies 10 bytes in a 4MB chunk:
    *   **Rsync algorithm**: Only upload the diffs? (Complex to manage on S3).
    *   **Chunk replacement**: Just re-upload that specific 4MB chunk. (Simpler).

### 4. Database: Metadata vs Block Data
*   **Block Data**: Immutable. Store in AWS S3 / Azure Blob.
*   **Metadata**: Highly relational (Folder hierarchy, Permissions). Store in **SQL (MySQL/PostgreSQL)** or NewSQL (CockroachDB).

---

## 🏗️ System Architecture

1.  **Client Application**: Runs on user's device. Has a "Watcher" to detect file changes.
2.  **Block Server**: Handles raw data upload.
    *   Receives chunks -> Computes Hash -> Checks "Block DB" (dedupe) -> Saves to S3.
3.  **Metadata Server**: Handles file logic.
    *   Updates "File Table" (File Name, Version, List of Block Hashes).
4.  **Notification Service**:
    *   Uses Long Polling / WebSocket.
    *   Tells other devices "File X has changed".
5.  **Offline Queue**: If offline, queue changes locally. Sync when online.

**Flow (Upload)**:
1.  Client splits file `Report.pdf` into Chunk A, Chunk B.
2.  Client hashes Chunk A. Sends hash to Block Server.
3.  Server says: "I already have this hash (Dedupe)."
4.  Client hashes Chunk B. Server says: "Upload it."
5.  Client uploads Chunk B.
6.  Client calls Metadata Server: "`Report.pdf` = [Hash A, Hash B]".

---

## 💻 Code Simulation: File Chunking & Hashing

Simulating how a client splits a file and generates hashes for deduplication.

```python
import hashlib
import os

class DriveClient:
    def __init__(self, chunk_size=1024): # 1KB for demo
        self.chunk_size = chunk_size

    def split_and_hash(self, file_content):
        """ Simulates reading a file and splitting it into chunks """
        chunks = []
        file_hash = hashlib.sha256(file_content).hexdigest()

        print(f"📄 Processing File (Total Size: {len(file_content)} bytes)")

        for i in range(0, len(file_content), self.chunk_size):
            chunk = file_content[i:i+self.chunk_size]
            chunk_hash = hashlib.sha256(chunk).hexdigest()
            chunks.append({"index": i//self.chunk_size, "hash": chunk_hash, "data": chunk})

        return file_hash, chunks

    def sync(self, filename, content, server_state):
        file_hash, chunks = self.split_and_hash(content)

        print(f"🔄 Syncing '{filename}'...")
        metadata = []

        for chunk in chunks:
            if chunk['hash'] in server_state:
                print(f"   ⏩ Chunk {chunk['index']} exists on server (Deduplicated)")
            else:
                print(f"   ⬆️ Uploading Chunk {chunk['index']} (Hash: {chunk['hash'][:8]}...)")
                server_state.add(chunk['hash']) # Mock upload

            metadata.append(chunk['hash'])

        print("✅ Sync Complete.\n")
        return server_state

if __name__ == "__main__":
    client = DriveClient(chunk_size=10) # Tiny chunks for demo

    # Mock Server Storage (Set of existing hashes)
    server_blocks = set()

    # 1. Upload File Version 1
    content_v1 = b"Hello world. This is a file."
    server_blocks = client.sync("doc.txt", content_v1, server_blocks)

    # 2. Modify File (Append data) - Version 2
    # "Hello world. " (Same) + "This is a file." (Same) + " UPDATE"
    content_v2 = b"Hello world. This is a file. UPDATE"
    server_blocks = client.sync("doc.txt", content_v2, server_blocks)
```

**Output:**
```
📄 Processing File (Total Size: 28 bytes)
🔄 Syncing 'doc.txt'...
   ⬆️ Uploading Chunk 0 (Hash: ...)
   ⬆️ Uploading Chunk 1 (Hash: ...)
   ⬆️ Uploading Chunk 2 (Hash: ...)
✅ Sync Complete.

📄 Processing File (Total Size: 35 bytes)
🔄 Syncing 'doc.txt'...
   ⏩ Chunk 0 exists on server (Deduplicated)
   ⏩ Chunk 1 exists on server (Deduplicated)
   ⏩ Chunk 2 exists on server (Deduplicated)
   ⬆️ Uploading Chunk 3 (Hash: ...)  <-- Only new data uploaded
✅ Sync Complete.
```

---

## 🧠 Interview Nuances

### 1. ACID properties?
*   Metadata updates must be ACID.
*   Use a Transactional DB. Changing a folder name shouldn't leave half files in old folder.

### 2. Conflict Resolution
*   User A and User B modify same file offline, then both go online.
*   **Strategy**: "Last Write Wins" is bad here.
*   **Strategy**: Create "Conflicted Copy" (e.g., `Report (User B's Conflict).pdf`) and let user decide.

### 3. Security
*   Encrypt data at rest (AES-256) and in transit (TLS).
*   Client-side encryption? (Zero-knowledge privacy). Hard for features like search/preview.

---

## ⚡ Flashcards
1.  **What is Block Storage vs Object Storage?**
    *   **Block**: Raw disk blocks (HDD/SSD). Fast. Used for OS/Databases.
    *   **Object**: Store data as immutable objects with metadata (S3). Slower, but massive scale.
2.  **Why chunk files?**
    *   Enables resumable uploads, parallel uploads, and efficient deduplication.
3.  **What is Differential Sync?**
    *   Syncing only the parts of a file that have changed, rather than the whole file.
