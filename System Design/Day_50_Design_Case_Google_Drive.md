# Day 50: Design Case - Google Drive / Dropbox

## 🎯 Goal
Design a file storage and synchronization service (Cloud Storage).

---

## 🗣️ Requirements

### Functional
1.  **File Operations**: Upload, Download, Update, Delete.
2.  **Sync**: Changes on one device should reflect on others automatically.
3.  **Versioning**: Restore previous versions.
4.  **Sharing**: Share files with other users.

### Non-Functional
1.  **Reliability**: Never lose data (99.999999999% durability).
2.  **Bandwidth Efficiency**: Don't re-upload the whole 1GB file if only 1 byte changed.
3.  **Scalability**: Billions of files.

---

## 📐 Capacity Estimation
*   **Users**: 100 Million DAU.
*   **Storage**: Avg 10GB/user -> 1 Exabyte (EB).
*   **Throughput**: Heavy write/read load.

---

## 🧠 Core Design Decisions

### 1. Block-Level Storage (Chunking)
*   **Problem**: Uploading a modified 1GB file takes forever.
*   **Solution**: Split files into blocks (e.g., 4MB).
    *   Calculate Hash (SHA-256) for each block.
    *   **Deduplication**: If User A and User B both have "The Avengers.mp4", we store the blocks only once.
    *   **Differential Sync**: Only upload changed blocks.

### 2. Metadata Database
*   Separation of Metadata and Block Data.
*   **Metadata DB (MySQL/Postgres)**: Stores file hierarchy, permissions, and "File X consists of Blocks [A, B, C]".
*   **Block Store (S3)**: Stores the actual immutable data blobs.

### 3. Synchronization (Long Polling)
*   Client needs to know when a file changes.
*   **Long Polling**: Client maintains a connection to Notification Service.
*   Server pushes "Change Event" -> Client requests metadata diff -> Client downloads new blocks.

---

## 🏗️ System Architecture

1.  **Client Application**:
    *   Watcher: Monitors local file system events.
    *   Chunker: Splits files.
    *   Indexer: Communicates with Metadata DB.
    *   Internal DB: Keeps track of local file state.

2.  **Metadata Service**:
    *   Authentication.
    *   Updates File Table (versions, pointers to blocks).
    *   Triggers Notification Service.

3.  **Block Storage (S3)**:
    *   Stores raw chunks.
    *   Addressable by Hash.

4.  **Cold Storage (Glacier)**:
    *   Move old versions or deleted files here to save cost.

---

## 💻 Code Simulation: Block Deduplication

Simulates how breaking files into blocks saves bandwidth and storage.

```python
import hashlib

class BlockStorage:
    def __init__(self):
        self.blocks = {} # hash -> content

    def store_block(self, content):
        h = hashlib.sha256(content.encode()).hexdigest()
        if h not in self.blocks:
            self.blocks[h] = content
            return h, True # True = New block
        return h, False # False = Duplicate

class DriveClient:
    def __init__(self, storage):
        self.storage = storage
        self.file_metadata = {} # filename -> [block_hashes]

    def upload_file(self, filename, content, block_size=10):
        print(f"📂 Uploading '{filename}'...")
        block_hashes = []
        new_blocks = 0

        # Split into blocks
        for i in range(0, len(content), block_size):
            chunk = content[i : i+block_size]
            h, is_new = self.storage.store_block(chunk)
            block_hashes.append(h)
            if is_new:
                new_blocks += 1

        self.file_metadata[filename] = block_hashes
        print(f"   ✅ Done. Total Blocks: {len(block_hashes)}, Uploaded: {new_blocks} (Deduplicated: {len(block_hashes)-new_blocks})")

# Simulation Usage
if __name__ == "__main__":
    cloud_storage = BlockStorage()
    client = DriveClient(cloud_storage)

    # 1. User A uploads a file
    file_v1 = "Hello World! This is a document."
    client.upload_file("doc.txt", file_v1, block_size=10)

    # 2. User A modifies the file slightly (Appends text)
    file_v2 = "Hello World! This is a document. v2"
    client.upload_file("doc_v2.txt", file_v2, block_size=10)

    # 3. User B uploads the same file as v1 (e.g., shared file)
    client.upload_file("doc_copy.txt", file_v1, block_size=10)
```

---

## 🧠 Interview Nuances

### 1. ACID properties in File Systems?
*   Metadata updates must be ACID.
*   If I move a folder, I expect it to be atomic.
*   **Conclusion**: Use a Relational DB for Metadata, not NoSQL (unless using something like DynamoDB with Transactions).

### 2. How to handle Conflicts?
*   User A and B edit the same file offline, then both go online.
*   **Strategy 1**: Last Write Wins (Bad for docs).
*   **Strategy 2**: Create "Conflicted Copy" (Dropbox style). Let user merge.

### 3. Security?
*   Encrypt blocks at rest.
*   Chunking helps security: Even if someone steals a block, they only have a random 4MB fragment, not the whole file.

---

## ⚡ Flashcards
1.  **What is Differential Sync?**
    *   Syncing only the parts of a file that changed, rather than the entire file. Achieved via block-level chunking.
2.  **Why use Long Polling for Drive?**
    *   Real-time updates are needed, but changes aren't as frequent as a Chat app. Long Polling is a good middle ground between Polling and WebSockets.
3.  **What is "Cold Storage"?**
    *   Cheap, slow-access storage (like AWS S3 Glacier) used for data that is rarely accessed (backups, old versions).
