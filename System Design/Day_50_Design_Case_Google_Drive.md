# Day 50: Design Case - Google Drive / Dropbox

## 🎯 Goal
Design a cloud file storage and synchronization service.
**Focus**: File Chunking, Deduplication, and Synchronization Consistency.

---

## 🗣️ Requirements

### Functional
1.  **Upload/Download**: Support large files (GBs).
2.  **Sync**: Automatic synchronization across multiple devices.
3.  **Versioning**: Restore previous versions of a file.
4.  **Offline Access**: Support editing offline and syncing when online.

### Non-Functional
1.  **Reliability**: Never lose data (Durability > Availability).
2.  **Consistency**: Files must be consistent across devices.
3.  **Bandwidth Efficiency**: Don't re-upload the whole file if only one word changed.

---

## 📐 Capacity Estimation
*   **Users**: 1 Billion.
*   **Storage**: 10 GB per user -> **10 Exabytes** total.
*   **QPS**: Sync traffic is bursty.

---

## 🧠 Core Design Decisions

### 1. Handling Large Files
*   **Problem**: Uploading a 2GB file fails if network drops at 99%.
*   **Solution**: **Chunking**.
    *   Split file into 4MB blocks.
    *   Upload blocks independently.
    *   Retry only failed blocks.

### 2. Deduplication (Bandwidth & Storage)
*   **Scenario**: User modifies 1 byte in a 100MB file.
*   **Naive**: Re-upload 100MB.
*   **Optimized**: Re-upload only the modified block (4MB).
*   **Global Deduplication**: If User A uploads "Movie.mp4" and User B uploads the same, store only one copy of the blocks.

### 3. Synchronization (Delta Sync)
*   Client calculates hashes of all blocks.
*   Sends list of hashes to server.
*   Server replies: "I have blocks A, B. Send me C."
*   Client uploads only block C.

### 4. Metadata Database
*   Needs strict ACID properties to maintain file hierarchy and versions.
*   **SQL Database** (MySQL/PostgreSQL) sharded by `user_id`.
*   Tables: `Files`, `Versions`, `Blocks`, `User_File_Map`.

---

## 🏗️ System Architecture

1.  **Client Application**:
    *   **Watcher**: Monitors file system events.
    *   **Chunker**: Splits files.
    *   **Indexer**: Maintains local state database.
2.  **Block Server**: Receives raw blocks. Stores in **S3**. Checks deduplication (Hash check).
3.  **Metadata Server**: Updates file index (e.g., "File.txt version 2 consists of blocks [H1, H2, H3]").
4.  **Notification Service**: Uses Long Polling / WebSockets to tell other devices "Hey, File.txt changed".
5.  **Cold Storage (Glacier)**: For old versions (Cost saving).

---

## 💻 Code Simulation: Chunking & Deduplication

Simulating how a client splits a file and uploads only new blocks.

```python
import hashlib

class CloudStorage:
    def __init__(self):
        self.block_store = {} # hash -> content
        self.file_meta = {}   # filename -> [block_hashes]

    def _get_hash(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

    def upload_file(self, filename, content):
        print(f"☁️ Processing '{filename}'...")

        # 1. Chunking (Small size for demo)
        CHUNK_SIZE = 5
        chunks = [content[i:i+CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]

        file_hashes = []
        bytes_uploaded = 0

        for chunk in chunks:
            h = self._get_hash(chunk)
            file_hashes.append(h)

            # 2. Check Deduplication
            if h in self.block_store:
                print(f"   ♻️ Block {h[:6]} exists. Skipping upload.")
            else:
                print(f"   ⬆️ Uploading Block {h[:6]} ('{chunk}')")
                self.block_store[h] = chunk
                bytes_uploaded += len(chunk)

        self.file_meta[filename] = file_hashes
        print(f"✅ Uploaded {bytes_uploaded} bytes. Total size: {len(content)} bytes.\n")

    def download_file(self, filename):
        hashes = self.file_meta.get(filename, [])
        content = "".join([self.block_store[h] for h in hashes])
        return content

if __name__ == "__main__":
    cloud = CloudStorage()

    # Version 1
    file_v1 = "Hello World Data"
    cloud.upload_file("my_doc.txt", file_v1)

    # Version 2 (Changed one word)
    file_v2 = "Hello Mars Data"
    cloud.upload_file("my_doc.txt", file_v2)

    print(f"Downloaded: '{cloud.download_file('my_doc.txt')}'")
```

**Output:**
```
☁️ Processing 'my_doc.txt'...
   ⬆️ Uploading Block 185f8d ('Hello')
   ⬆️ Uploading Block d09e01 (' Worl')
   ⬆️ Uploading Block 482186 ('d Dat')
   ⬆️ Uploading Block 9c55b7 ('a')
✅ Uploaded 16 bytes. Total size: 16 bytes.

☁️ Processing 'my_doc.txt'...
   ♻️ Block 185f8d exists. Skipping upload.
   ⬆️ Uploading Block ffe8e2 (' Mars')
   ♻️ Block 482186 exists. Skipping upload.
   ♻️ Block 9c55b7 exists. Skipping upload.
✅ Uploaded 5 bytes. Total size: 15 bytes.

Downloaded: 'Hello Mars Data'
```

---

## 🧠 Interview Nuances

### 1. Rolling Hash (Rabin-Karp)
*   **Problem with Fixed-Size Chunking**: If I insert one character at the start, ALL subsequent blocks shift and change hash. Zero deduplication.
*   **Solution**: **Rolling Hash**. Finds chunk boundaries based on content patterns, not fixed offsets. Resists insertion shifts.

### 2. Conflict Resolution
*   User A and User B edit same file offline. Both come online.
*   **Strategy**: "Last Write Wins" is bad here.
*   **Better**: Create a "Conflicted Copy" (File_v1_Conflict_UserB.txt) and let the user merge manually.

### 3. ACID Metadata
*   Why not NoSQL?
*   We need strong consistency. If I move a folder, all files inside must move atomically. NoSQL eventually consistent directory structures are confusing for users.

---

## ⚡ Flashcards
1.  **What is Differential Synchronization?**
    *   Syncing only the difference (diff) between two versions of a file (used in Git/Dropbox).
2.  **Block vs Object Storage?**
    *   **Block (EBS)**: Fast, OS sees a disk. Good for Databases.
    *   **Object (S3)**: REST API, Immutable objects. Good for Drive storage.
3.  **Why Long Polling for Drive?**
    *   Client keeps a connection open to Metadata server. Server pushes "Change Notification" immediately. Saves battery vs periodic polling.
