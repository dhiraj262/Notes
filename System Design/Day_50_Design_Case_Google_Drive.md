# Day 50: Design Case - Google Drive / Dropbox

## 🎯 Goal
Design a file hosting service that synchronizes files across multiple devices.
**Focus**: Data consistency, Block-level storage, and Deduplication.

---

## 🗣️ Requirements

### Functional
1.  **Add/Update/Delete**: Files synced to cloud and other devices.
2.  **Versioning**: Restore previous versions.
3.  **Offline Access**: Work locally, sync when online.
4.  **Sharing**: Share file with other users.

### Non-Functional
1.  **Reliability**: Never lose data (11 nines durability).
2.  **Speed**: Sync changes quickly. Don't re-upload entire 1GB file for 1 byte change.
3.  **Consistency**: Devices should see same view.

---

## 📐 Capacity Estimation
*   **Users**: 500M.
*   **Storage**: 10GB/user -> 5 Exabytes (Huge).
*   **Traffic**: Read/Write ratio ~ 1:1 (Sync traffic).

---

## 🧠 Core Design Decisions

### 1. File Handling: Chunking
*   **Problem**: Uploading a 2GB file takes forever. Retrying on failure is painful.
*   **Solution**: Split file into **Chunks** (e.g., 4MB).
    *   Upload chunks in parallel.
    *   If chunk fails, retry only that chunk.

### 2. Deduplication (Block Level)
*   **Problem**: 1000 users upload "Batman_Movie.mp4". Storing 1000 copies is wasteful.
*   **Solution**: Hash each chunk (SHA-256).
    *   If Hash exists in DB, don't upload bytes. Just link User to existing chunk.
    *   Saves ~30-50% storage.

### 3. Delta Sync (Rsync logic)
*   If user modifies 1 sentence in a document, only the chunk containing that sentence changes.
*   Client uploads only the new chunk.

---

## 🏗️ System Architecture

1.  **Client Application**:
    *   **Watcher**: Monitors file system events.
    *   **Chunker**: Splits files.
    *   **Indexer**: Local DB of file state.
2.  **Metadata Database** (MySQL/Postgres):
    *   Stores File hierarchy (Names, Folders) and mapping to Chunks.
    *   Table: `FileID | ChunkHash | Order`.
3.  **Block Server**:
    *   Receives raw bytes.
    *   Stores to **S3/Cold Storage**.
4.  **Notification Service**:
    *   Long polling / WebSocket.
    *   Tells other devices: "File X changed, download new chunks".

---

## 💻 Code Simulation: Chunking & Deduplication

```python
import hashlib

class CloudStorage:
    def __init__(self):
        self.block_store = {} # Hash -> Data
        self.file_metadata = {} # Filename -> [Hash1, Hash2...]

    def upload_file(self, filename, content):
        print(f"📂 Processing {filename}...")
        chunks = self._chunk_content(content)
        chunk_hashes = []

        for chunk in chunks:
            h = hashlib.sha256(chunk.encode()).hexdigest()
            chunk_hashes.append(h)

            if h not in self.block_store:
                print(f"   ⬆️ Uploading new chunk: {h[:8]}...")
                self.block_store[h] = chunk
            else:
                print(f"   ♻️ Deduped chunk: {h[:8]}...")

        self.file_metadata[filename] = chunk_hashes
        print("   ✅ File Saved.")

    def _chunk_content(self, content, size=5):
        return [content[i:i+size] for i in range(0, len(content), size)]

    def download_file(self, filename):
        hashes = self.file_metadata.get(filename, [])
        content = ""
        for h in hashes:
            content += self.block_store[h]
        return content

if __name__ == "__main__":
    cloud = CloudStorage()

    # User 1 uploads
    cloud.upload_file("resume.txt", "Hello World This is Resume")

    # User 2 uploads same file (Dedup)
    cloud.upload_file("resume_copy.txt", "Hello World This is Resume")

    # User 3 uploads modified version
    cloud.upload_file("resume_v2.txt", "Hello World This is NEW!!!")

    print(f"\nDownloaded: {cloud.download_file('resume_v2.txt')}")
```

---

## 🧠 Interview Nuances

### 1. Conflict Resolution?
*   User A and B edit same file offline. Both come online.
*   **Strategy**: Create "Conflicted Copy". Let user manually merge. (Git style merging is too complex for general users).

### 2. ACID for Metadata?
*   Moving a file from Folder A to B must be atomic.
*   Use Relational DB (ACID) for Metadata, not NoSQL.

### 3. Trash / Recovery?
*   Don't delete chunks immediately. Mark as "Orphaned".
*   Run Garbage Collection (GC) cron job every 30 days to remove chunks not referenced by any file version.

---

## ⚡ Flashcards
1.  **What is Delta Sync?**
    *   Synchronizing only the parts of a file that have changed, rather than the whole file.
2.  **Why separate Metadata from Block Storage?**
    *   Metadata (small, relational, needs ACID) scales differently than Block Data (huge, immutable, needs Blob store).
3.  **What is Long Polling?**
    *   Client asks server "Any updates?". Server holds the request open until an update is available, then responds. Used for real-time sync.
