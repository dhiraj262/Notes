# Day 50: Design Case - File Storage (Google Drive/Dropbox)

## 🎯 Goal
Design a cloud file storage and synchronization service.
**Focus**: Consistency (Sync), Reliability (Data Durability), and Bandwidth Efficiency.

---

## 🗣️ Requirements

### Functional
1.  **Upload/Download**: Support huge files.
2.  **Sync**: Changes on one device appear on others.
3.  **Versioning**: Keep history of changes.
4.  **Sharing**: Share files with other users (Permissions).

### Non-Functional
1.  **Reliability**: 99.999999999% (11 9s) durability. Never lose data.
2.  **ACID**: Metadata must be consistent.
3.  **Efficiency**: Don't re-upload the whole file if only 1 byte changed.

---

## 📐 Capacity Estimation
*   **Users**: 100 Million DAU.
*   **Storage**: 10GB/User -> 1 Exabyte (EB) total.
*   **QPS**: Sync traffic is bursty.

---

## 🧠 Core Design Decisions

### 1. Chunking & Deduplication
*   **Problem**: Uploading a 1GB file for a 1KB change is wasteful.
*   **Solution**: Split file into **4MB Blocks**.
    *   Calculate Hash (SHA-256) of each block.
    *   If Hash exists in DB, don't upload (Deduplication).
    *   Only upload new blocks.
*   **Result**: Saves bandwidth and storage.

### 2. Metadata vs Block Storage
*   **Block Server**: Stores raw chunks in S3/Object Storage. Immutable.
*   **Metadata DB**: Stores file structure (File Path -> List of Block Hashes).
    *   Needs ACID. Use SQL (Postgres/Spanner).

### 3. Synchronization (Client-Side)
*   **Long Polling**: Client keeps a connection open to Notification Service.
*   When Server updates, it pushes a "Change Notification" to client.
*   Client pulls the new metadata and downloads only changed blocks.

---

## 🏗️ System Architecture

1.  **Block Server**:
    *   Receives raw blocks.
    *   Calculates Hash.
    *   Stores to S3: `bucket/hash_xyz`.
2.  **Metadata Service**:
    *   API for `create_file`, `update_file`, `list_files`.
    *   Updates SQL DB.
3.  **Notification Service**:
    *   WebSocket/Long-Polling.
    *   Notifies other devices of the same user.
4.  **Cold Storage**:
    *   Move old versions/deleted files to Glacier (cheaper).

---

## 💻 Code Simulation: Deduplication Logic

Simulating how a file is split into blocks and deduplicated based on hash.

```python
import hashlib

class FileStorage:
    def __init__(self):
        self.block_store = {} # hash -> content (Simulated S3)
        self.file_metadata = {} # filename -> [block_hashes] (Simulated SQL)

    def upload_file(self, filename, content):
        print(f"📂 Uploading: {filename} ({len(content)} chars)")

        # Split into fixed-size blocks (e.g., 4 chars for demo)
        block_size = 4
        blocks = [content[i:i+block_size] for i in range(0, len(content), block_size)]

        block_hashes = []
        for block in blocks:
            h = hashlib.md5(block.encode()).hexdigest()
            if h in self.block_store:
                print(f"   ♻️ Deduplicated Block: {block} ({h[:6]}...)")
            else:
                self.block_store[h] = block
                print(f"   💾 New Block Stored: {block} ({h[:6]}...)")
            block_hashes.append(h)

        self.file_metadata[filename] = block_hashes
        print("   ✅ Upload Complete.\n")

    def download_file(self, filename):
        print(f"📥 Downloading: {filename}")
        hashes = self.file_metadata.get(filename, [])
        content = ""
        for h in hashes:
            content += self.block_store.get(h, "")
        return content

if __name__ == "__main__":
    storage = FileStorage()

    # User A uploads a file
    storage.upload_file("thesis_v1.txt", "Hello World This is Data")

    # User A modifies slightly (Appending)
    storage.upload_file("thesis_v2.txt", "Hello World This is Date")

    print(f"Stored v1: {storage.download_file('thesis_v1.txt')}")
    print(f"Stored v2: {storage.download_file('thesis_v2.txt')}")
```

**Output:**
```
📂 Uploading: thesis_v1.txt (24 chars)
   💾 New Block Stored: Hell (1824e8...)
   💾 New Block Stored: o Wo (57960f...)
   💾 New Block Stored: rld  (ca022a...)
   💾 New Block Stored: This (77631c...)
   💾 New Block Stored:  is  (b188b7...)
   💾 New Block Stored: Data (f6068d...)
   ✅ Upload Complete.

📂 Uploading: thesis_v2.txt (24 chars)
   ♻️ Deduplicated Block: Hell (1824e8...)
   ♻️ Deduplicated Block: o Wo (57960f...)
   ♻️ Deduplicated Block: rld  (ca022a...)
   ♻️ Deduplicated Block: This (77631c...)
   ♻️ Deduplicated Block:  is  (b188b7...)
   💾 New Block Stored: Date (447497...)
   ✅ Upload Complete.

📥 Downloading: thesis_v1.txt
Stored v1: Hello World This is Data
📥 Downloading: thesis_v2.txt
Stored v2: Hello World This is Date
```

---

## 🧠 Interview Nuances

### 1. Differential Sync (rsync)?
*   If I change 1 byte in the *middle* of a 4MB block, the hash changes, and I re-upload 4MB.
*   **Optimization**: Use Rolling Hashes (Rabin-Karp) to find exact byte boundaries. Or simple "Delta Sync" for text files.

### 2. How to handle Conflicts?
*   Two devices edit `file.txt` offline.
*   **Strategy**: "Last Write Wins" (bad for data loss) or "Create Conflicted Copy" (Dropbox style).

### 3. Trash/Recycle Bin?
*   Don't delete blocks immediately. Mark metadata as `deleted`.
*   Run Garbage Collection job every 30 days to remove orphan blocks (blocks not referenced by any file).

---

## ⚡ Flashcards
1.  **What is Block Storage?**
    *   Splitting data into fixed-size chunks (blocks) and storing them individually. Allows for deduplication and parallel transfers.
2.  **Why use Long Polling for Sync?**
    *   It reduces server load compared to short polling (asking "any updates?" every second) while still providing near real-time updates.
3.  **What is ACID?**
    *   Atomicity, Consistency, Isolation, Durability. Crucial for the Metadata Database to ensuring file structure is never corrupted.
