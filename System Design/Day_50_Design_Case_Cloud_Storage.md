# Day 50: Design Google Drive (Cloud Storage)

## 🎯 Goal
Design a Cloud Storage service (like Google Drive or Dropbox) that allows users to store, sync, and share files across multiple devices with version history.

## 📋 Requirements

### Functional
1.  **File Storage**: Upload/Download files.
2.  **File Sync**: Automatic sync across devices.
3.  **Versioning**: Keep history of changes.
4.  **Sharing**: Share files via link/email.
5.  **Offline Support**: Edit offline, sync when online.

### Non-Functional
1.  **Reliability**: Data durability is paramount (99.999999999%).
2.  **Bandwidth Efficiency**: Only sync changes (Delta Sync).
3.  **Scalability**: Billions of files.

## 🔢 Capacity Estimation

*   **Users**: 100 Million DAU.
*   **Storage**: 10 GB avg/user -> 1 Exabyte (1000 PB).
*   **QPS**: Uploads/Downloads are less frequent but heavy. Sync traffic is "chatty".

## 🏗️ Architecture Design

### 1. Block-Level Storage (The Core)
We do not store files as whole objects (except for very small ones).
*   **Chunking**: Split files into blocks (e.g., 4MB).
*   **Compression**: Compress each block.
*   **Encryption**: Encrypt each block.
*   **Storage**: Store blocks in **S3/Blob Storage** (immutable).
*   **Metadata DB**: Stores the file structure (`FileID -> [BlockID_1, BlockID_2, ...]`).

### 2. Deduplication
If User A uploads `Batman.mp4` and User B uploads the same file:
*   **Hash Check**: Calculate hash (SHA-256) of each block.
*   If block hash exists in S3, do not upload again. Just point User B's file metadata to the existing block.
*   *Savings*: Massive (40-60% storage saving).

### 3. Synchronization (Delta Sync)
*   **Scenario**: User changes one sentence in a 10MB Word doc.
*   **Naive Approach**: Re-upload 10MB. (Bad)
*   **Delta Sync**:
    1.  Client breaks file into blocks.
    2.  Calculates hashes.
    3.  Sends list of hashes to server.
    4.  Server says: "I have blocks A, B, D. I need block C."
    5.  Client uploads only block C.

### 4. Metadata Database
Needs to handle file hierarchy (Folders) and Versions.
*   **SQL (Postgres/MySQL)**: Good for ACID compliance (moving files, renaming).
*   **Schema**:
    *   `Users` table.
    *   `Workspaces` table.
    *   `Files` table (id, parent_id, is_folder, latest_version).
    *   `Versions` table (file_id, version_num, block_list_json).

## 🐍 Code Simulation
Python simulation of **File Chunking and Deduplication**.

```python
import hashlib

class BlockStorage:
    def __init__(self):
        self.block_store = {} # hash -> data (Simulating S3)
        self.files = {} # filename -> [block_hashes] (Simulating Metadata DB)

    def _get_hash(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

    def upload_file(self, filename, content, chunk_size=4):
        print(f"[Client] Uploading '{filename}'...")
        blocks = []
        # Chunking logic
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            h = self._get_hash(chunk)

            # Deduplication Check
            if h not in self.block_store:
                print(f"   -> New Block {h[:6]}: '{chunk}' uploaded.")
                self.block_store[h] = chunk
            else:
                print(f"   -> Dedup! Block {h[:6]} already exists.")

            blocks.append(h)

        self.files[filename] = blocks
        print(f"[Server] File '{filename}' saved with {len(blocks)} blocks.\n")

    def download_file(self, filename):
        if filename not in self.files:
            return None

        content = ""
        for h in self.files[filename]:
            content += self.block_store[h]
        return content

# --- Driver Code ---
if __name__ == "__main__":
    storage = BlockStorage()

    # User A uploads a file
    file1_content = "Hello World This is Data"
    storage.upload_file("doc1.txt", file1_content)

    # User B uploads a slightly modified version
    # "Hello World " is same. "That " is new. "is Data" is same.
    file2_content = "Hello World That is Data"
    storage.upload_file("doc2.txt", file2_content)

    # Verify storage savings
    total_blocks = len(storage.block_store)
    print(f"Total Unique Blocks Stored: {total_blocks}")
```

## 🧠 Interview Nuances

### "The Trap": Strong Consistency for Sync
*   **Problem**: If User A and User B edit the same file offline and come online?
*   **Solution**: **Differential Synchronization** or simple "Last Write Wins" with a "Conflicted Copy" created for the loser. Google Docs uses **Operational Transformation (OT)** or **CRDTs** for real-time collab, but Drive file sync usually uses version vectors.

### "The Kill Shot": Security (End-to-End Encryption)
*   **Challenge**: "Can Google engineers read my files?"
*   **Solution**:
    *   **Standard**: Encrypted at rest (Server holds key).
    *   **Zero-Knowledge (Tresorit/Mega)**: Client encrypts before upload. Server never sees the key. This kills Deduplication (hashes are random) unless utilizing "Convergent Encryption".

### "Production Realities"
*   **Cold Storage**: Old versions of files (e.g., v1 from 3 years ago) should be moved to **Glacier/Deep Archive** to save costs.
*   **Notification Service**: Use Long Polling (or WebSocket) to notify other devices "File X changed, download now".

## ⚡ Flashcards
*   **Save Bandwidth?** -> Delta Sync (Block level).
*   **Save Storage?** -> Deduplication (Content Addressable Storage).
*   **DB for Metadata?** -> SQL (Strong consistency for file moves).
*   **Durability?** -> Erasure Coding + Replication.
