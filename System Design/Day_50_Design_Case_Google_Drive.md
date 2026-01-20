# Day 50: Design Case - Google Drive / Dropbox

## 🎯 Goal
Design a cloud file storage and synchronization service.
**Focus**: File Chunking, Deduplication, Synchronization, and Consistency.

---

## 🗣️ Requirements

### Functional
1.  **Upload/Download**: Support huge files.
2.  **Sync**: Changes on one device appear on others.
3.  **Versioning**: Keep history of changes.
4.  **Sharing**: Access control lists (ACL).

### Non-Functional
1.  **Reliability**: 99.999999999% durability (11 nines).
2.  **Efficiency**: Don't re-upload the whole 1GB file for a 1-byte change.
3.  **ACID**: Metadata (folder structure) must be consistent.

---

## 📐 Capacity Estimation
*   **Users**: 1 Billion.
*   **Storage**: 10GB free -> Exabytes of data.
*   **Traffic**: Heavy upload/download bandwidth.

---

## 🧠 Core Design Decisions

### 1. File Handling: Block Storage
*   Uploading a single 5GB file as one object is bad. (Network fail = restart 0%).
*   **Chunking**: Split file into fixed-size blocks (e.g., 4MB).
*   **Content-Addressed Storage (CAS)**:
    *   Name of the block = Hash(Content).
    *   If two users upload the same "Matrix.mp4", we store it only once (Deduplication).

### 2. Synchronization: Delta Sync
*   **Rsync Algorithm**: If I change one word in a Word Doc.
    *   Client calculates hashes of new chunks.
    *   Compares with server.
    *   Only uploads the *new* chunk.

### 3. Metadata Database
*   Files are chunks in S3. But "Folders" are just metadata.
*   **Structure**: Hierarchy.
*   **DB**: Relational (PostgreSQL) is best for ACID (Moving a folder should be atomic).
    *   Table: `Files` (id, name, parent_id, is_folder).
    *   Table: `Versions` (file_id, version_num, list_of_chunk_hashes).

---

## 🏗️ System Architecture

1.  **Block Server**:
    *   Handles raw data upload.
    *   Checks "Does Hash X exist?". If yes -> Skip upload (Dedup).
    *   Stores to **S3/Cold Storage**.
2.  **Metadata Server**:
    *   Handles "Rename", "Move", "List".
    *   Updates the SQL DB.
3.  **Notification Service**:
    *   Long Polling / WebSocket.
    *   Tells other devices "File X changed, download new version".
4.  **Offline Client**:
    *   Queues changes locally (SQLite).
    *   Syncs when online.

---

## 💻 Code Simulation: Chunking & Deduplication

Simulating how splitting a file allows reusing existing blocks.

```python
import hashlib

class FileChunker:
    def __init__(self, chunk_size=4096):
        self.chunk_size = chunk_size
        self.storage = {} # Hash -> Data (Mock S3)

    def upload_file(self, filename, content):
        print(f"📂 Uploading {filename} ({len(content)} bytes)...")
        hashes = []

        # Split into chunks
        for i in range(0, len(content), self.chunk_size):
            chunk = content[i : i + self.chunk_size]

            # Calculate Hash
            h = hashlib.sha256(chunk.encode()).hexdigest()[:8] # Short hash

            # Dedup Check
            if h in self.storage:
                print(f"   ♻️ Deduplicated chunk {h}")
            else:
                self.storage[h] = chunk
                print(f"   💾 Stored new chunk {h}")

            hashes.append(h)

        return hashes

    def reconstruct(self, chunk_hashes):
        data = ""
        for h in chunk_hashes:
            data += self.storage[h]
        return data

if __name__ == "__main__":
    system = FileChunker(chunk_size=10)

    # 1. Upload File A
    file_a = "Hello World This is Data."
    meta_a = system.upload_file("Doc1.txt", file_a)

    # 2. Upload File B (Minor change)
    file_b = "Hello World This is Date." # 'Data' -> 'Date'
    meta_b = system.upload_file("Doc2.txt", file_b)

    # 3. Verify
    print(f"\nReconstructed Doc1: {system.reconstruct(meta_a)}")
    print(f"Reconstructed Doc2: {system.reconstruct(meta_b)}")
```

**Output:**
```
📂 Uploading Doc1.txt (25 bytes)...
   💾 Stored new chunk 12fec4c6
   💾 Stored new chunk 0d9c0657
   💾 Stored new chunk cbc922fe
📂 Uploading Doc2.txt (25 bytes)...
   ♻️ Deduplicated chunk 12fec4c6
   ♻️ Deduplicated chunk 0d9c0657
   💾 Stored new chunk a20fd326

Reconstructed Doc1: Hello World This is Data.
Reconstructed Doc2: Hello World This is Date.
```

---

## 🧠 Interview Nuances

### 1. Conflict Resolution
*   Alice and Bob edit same file offline. Both sync. Who wins?
*   **Strategy**: Create "Conflicted Copy". Let user decide.
*   **Google Docs**: Uses Operational Transformation (OT) or CRDTs for real-time merge. (Different complexity).

### 2. Security (Encryption)
*   **At Rest**: S3 Server Side Encryption.
*   **E2EE**: Encrypt on client. Server sees garbage. (Key management is hard).

### 3. Trash / Recovery
*   Don't delete chunks immediately. Mark as "Orphaned".
*   Garbage Collector (Cron job) runs weekly to delete chunks not referenced by any file version.

---

## ⚡ Flashcards
1.  **What is Block-Level Deduplication?**
    *   Storing only unique blocks of data across all users to save massive amounts of space.
2.  **Why use SQL for Metadata?**
    *   File systems are hierarchical and require strong consistency (ACID) for move/rename operations.
3.  **How to handle large file uploads?**
    *   Multipart Upload (S3). Upload parts in parallel. Retry failed parts only.
