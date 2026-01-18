# Day 50: Design Case - Google Drive / Dropbox

## 🎯 Goal
Design a file storage and synchronization service.
**Focus**: File Chunking, Deduplication, and Synchronization (Client-Server).

---

## 🗣️ Requirements

### Functional
1.  **Upload/Download**: Drag and drop files.
2.  **Sync**: Auto-update across devices.
3.  **Versioning**: Restore previous versions.
4.  **Sharing**: Generate public links.

### Non-Functional
1.  **Reliability**: Data durability (99.999999999%).
2.  **Bandwidth Efficiency**: Don't re-upload the whole file if only 1 byte changed.
3.  **Scale**: 10M DAU. 50GB storage/user.

---

## 📐 Capacity Estimation
*   **Total Users**: 100M.
*   **Total Storage**: 100M * 10GB (avg) = 1 Exabyte.
*   **Block Storage**: Storing files as objects (S3) is standard.
*   **Metadata DB**: Needs to handle massive scale (Trillions of file objects).

---

## 🏗️ System Architecture

### 1. The Client (Magic happens here)
*   **Watcher**: Monitors file system for changes.
*   **Chunker**: Splits files into chunks (e.g., 4MB).
*   **Hasher**: SHA-256 of each chunk.
*   **Sync Logic**:
    *   If `file.txt` changes, calculate hash of new chunks.
    *   Compare with server. Only upload **new/changed chunks**.

### 2. Block Server (Storage)
*   Receives raw chunks.
*   Stores them in **S3 / Ceph**.
*   Key = `Hash(Chunk)`. Value = `Binary Data`.

### 3. Metadata Database
*   Stores the file hierarchy (Folder structure).
*   `FileID` -> `List[ChunkHashes]`.
*   Needs Strong Consistency for syncing.
*   **SQL (MySQL)** with sharding is common, or a specialized consistent Key-Value store.

### 4. Deduplication
*   If User A uploads `movie.mp4` and User B uploads the same `movie.mp4`.
*   Both calculate same hashes.
*   Client B asks: "Do you have hash X?"
*   Server: "Yes."
*   Client B: "Okay, I won't upload. Just link my file to that chunk."
*   **Saves massive bandwidth and storage.**

---

## 💻 Code Simulation: Chunking & Deduplication

Simulating how files are split and deduplicated.

```python
import hashlib

class GoogleDrive:
    def __init__(self):
        self.chunk_store = {} # hash -> data
        self.file_metadata = {} # filename -> [hash_list]

    def upload_file(self, filename, content):
        print(f"📂 Uploading {filename}...")

        # 1. Chunking (Fixed size for simulation)
        chunk_size = 4
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

        chunk_hashes = []
        for chunk in chunks:
            # 2. Hashing
            h = hashlib.md5(chunk.encode()).hexdigest()
            chunk_hashes.append(h)

            # 3. Deduplication check
            if h in self.chunk_store:
                print(f"   ♻️ Chunk exists (Dedup): {chunk}")
            else:
                self.chunk_store[h] = chunk
                print(f"   💾 New Chunk saved: {chunk}")

        self.file_metadata[filename] = chunk_hashes
        print(f"✅ File {filename} saved.\n")

    def download_file(self, filename):
        hashes = self.file_metadata.get(filename)
        content = ""
        for h in hashes:
            content += self.chunk_store[h]
        print(f"📥 Downloaded {filename}: {content}")

if __name__ == "__main__":
    drive = GoogleDrive()

    # User 1 uploads
    drive.upload_file("resume.txt", "Hello world, this is my resume.")

    # User 2 uploads SAME content (Dedup should happen)
    drive.upload_file("copy_resume.txt", "Hello world, this is my resume.")

    # User 3 uploads partial match
    drive.upload_file("letter.txt", "Hello world, bye.")
```

**Output:**
```
📂 Uploading resume.txt...
   💾 New Chunk saved: Hell
   💾 New Chunk saved: o wo
   💾 New Chunk saved: rld,
   ...
✅ File resume.txt saved.

📂 Uploading copy_resume.txt...
   ♻️ Chunk exists (Dedup): Hell
   ... (All chunks deduped)
✅ File copy_resume.txt saved.

📂 Uploading letter.txt...
   ♻️ Chunk exists (Dedup): Hell
   ...
   💾 New Chunk saved:  bye
✅ File letter.txt saved.
```

---

## 🧠 Interview Nuances

### 1. Rolling Hash vs Fixed Size Chunking?
*   **Fixed Size**: If I insert one byte at the start, *all* subsequent chunks shift and change hash. Bad!
*   **Rolling Hash (Rabin-Karp)**: Window slides based on content. Boundary is determined by data pattern, not position.
*   **Result**: Inserting a byte only changes *one* chunk. Better for edits.

### 2. Metadata Consistency?
*   Syncing is hard.
*   Use a **Local Database** (SQLite) on the client to track state.
*   Use **Long Polling** or **WebSockets** for server to notify client of changes.

### 3. Namespace / Directory Structure?
*   Don't just store path strings.
*   Store `ParentID` pointers. Moving a folder is just changing one `ParentID`, not rewriting millions of paths.

---

## ⚡ Flashcards
1.  **What is ACID?**
    *   Atomicity, Consistency, Isolation, Durability. Crucial for the Metadata DB.
2.  **Block Storage vs Object Storage?**
    *   Block (Hard Drive): Fast, mutable.
    *   Object (S3): Slow, immutable, infinite scale. (Used here for chunks).
3.  **Delta Sync?**
    *   Synchronizing only the parts of the file that changed, not the whole file.
