# Day 49: Design Case - YouTube / Netflix

## 🎯 Goal
Design a global video streaming platform supporting uploads, transcoding, and low-latency playback.
**Scale**: 1 Billion hours of video watched daily.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload video files (MP4, MKV).
2.  **Transcoding**: Convert raw video into multiple formats (resolutions/codecs) for different devices.
3.  **Streaming**: Smooth playback with zero buffering (Adaptive Bitrate).

### Non-Functional
1.  **High Availability**: Videos must always be playable.
2.  **Scalability**: Handle viral videos (millions of concurrent viewers).
3.  **Performance**: Low latency start-up time.

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million.
*   **Storage**:
    *   500 hours of video uploaded per minute.
    *   1 min = 50MB (Raw). 500 * 60 * 50MB = 1.5 TB/hour.
    *   **Petabytes** of storage needed daily. (Use S3/Glacier).
*   **Bandwidth**:
    *   Massive outbound traffic. CDN costs are the biggest expense.

---

## 🧠 Core Design Decisions

### 1. Storage: Blob Store + CDN
*   **Raw Video**: Store in S3 (Cheap, durable).
*   **Processed Chunks**: Store in S3, but cache in **CDN** (Content Delivery Network - Cloudflare/Akamai).
*   **Why CDN?**: Moves content closer to the user (Edge servers). Reduces latency and buffers.

### 2. Transcoding (The Heavy Lifting)
*   Raw video (4K, 50GB) is too big to stream.
*   We need to convert it to: 1080p, 720p, 480p, 360p.
*   **DAG Model**: Split video into 5-minute segments. Process segments in parallel workers. Merge them back.

### 3. Adaptive Bitrate Streaming (DASH/HLS)
*   **Protocol**: HLS (HTTP Live Streaming) or MPEG-DASH.
*   How it works:
    *   Server splits video into 10-second chunks (`.ts` files).
    *   Creates a `manifest.m3u8` file listing chunks for all resolutions.
    *   **Player** detects user bandwidth. If slow, requests 360p chunk. If fast, switches to 1080p chunk seamlessly.

---

## 🏗️ System Architecture

1.  **Client** uploads video -> **Original Storage (S3)**.
2.  **Upload Service** triggers message to **Kafka**.
3.  **Transcoding Service** (Consumer):
    *   Downloads video. Splits into chunks.
    *   Transcodes to multiple formats (Parallel Processing).
    *   Uploads chunks to **S3** and **CDN**.
4.  **Metadata DB**: Stores "VideoID -> S3 URL".
5.  **Streaming**:
    *   User requests video.
    *   Server returns `manifest.m3u8`.
    *   User's player pulls chunks directly from **CDN**.

---

## 💻 Code Simulation: Upload & Transcode Flow

Simulating the workflow of uploading a raw video, transcoding it into chunks, and serving it via Adaptive Bitrate logic.

```python
class VideoProcessingService:
    def __init__(self):
        self.storage = {} # Mock S3
        self.cdn = {}     # Mock CDN

    def upload_raw_video(self, video_id, content):
        print(f"⬆️ Uploading raw video: {video_id}...")
        self.storage[f"raw_{video_id}"] = content
        print("   ✅ Upload Complete.")
        self.trigger_transcoding(video_id)

    def trigger_transcoding(self, video_id):
        print(f"⚙️ Transcoding started for {video_id}...")

        # Simulate generating different resolutions
        resolutions = ["480p", "720p", "1080p"]
        manifest = f"#EXTM3U\n#Video {video_id}"

        for res in resolutions:
            # Create chunk
            chunk_name = f"{video_id}_{res}.ts"
            self.storage[chunk_name] = f"[Binary Data for {res}]"

            # Push to CDN
            self.cdn[chunk_name] = self.storage[chunk_name]
            print(f"   🎥 Generated {res} chunk -> Pushed to CDN")

            manifest += f"\n#EXT-X-STREAM-INF:BANDWIDTH=...,RESOLUTION={res}\n{chunk_name}"

        # Save manifest
        self.cdn[f"{video_id}.m3u8"] = manifest
        print("   ✅ Transcoding & Distribution Complete.")

    def play_video(self, video_id, user_bandwidth):
        print(f"\n▶️ User requesting {video_id} (Bandwidth: {user_bandwidth})")
        manifest = self.cdn.get(f"{video_id}.m3u8")
        if not manifest:
            print("   ❌ Video not found.")
            return

        # Simple Adaptive Bitrate Logic
        if user_bandwidth == "HIGH":
            chosen = "1080p"
        elif user_bandwidth == "MEDIUM":
            chosen = "720p"
        else:
            chosen = "480p"

        chunk = f"{video_id}_{chosen}.ts"
        print(f"   📡 Streaming {chosen} chunk from CDN: {chunk}")

if __name__ == "__main__":
    netflix = VideoProcessingService()

    # 1. User Uploads
    netflix.upload_raw_video("movie_1", "Raw mp4 data")

    # 2. Users Watch
    netflix.play_video("movie_1", "HIGH")   # Fast Internet
    netflix.play_video("movie_1", "LOW")    # Slow Internet
```

**Output:**
```
⬆️ Uploading raw video: movie_1...
   ✅ Upload Complete.
⚙️ Transcoding started for movie_1...
   🎥 Generated 480p chunk -> Pushed to CDN
   🎥 Generated 720p chunk -> Pushed to CDN
   🎥 Generated 1080p chunk -> Pushed to CDN
   ✅ Transcoding & Distribution Complete.

▶️ User requesting movie_1 (Bandwidth: HIGH)
   📡 Streaming 1080p chunk from CDN: movie_1_1080p.ts

▶️ User requesting movie_1 (Bandwidth: LOW)
   📡 Streaming 480p chunk from CDN: movie_1_480p.ts
```

---

## 🧠 Interview Nuances

### 1. How to handle "Thundering Herd"?
*   When a new episode of a popular show drops, millions request it at once.
*   **CDN** handles 99% of this. But if CDN misses, Origin S3 might die.
*   **Solution**: **Request Collapsing** (CDN groups 1000 requests for the same file into 1 request to Origin).

### 2. Encryption (DRM)?
*   Netflix/Disney+ need to prevent piracy.
*   Use **AES Encryption** on chunks. The player needs a license key to decrypt and play.

### 3. Recommendations?
*   Use a separate **Machine Learning System** (Collaborative Filtering) to generate the "Home Screen" feed. (See Day 72).

---

## ⚡ Flashcards
1.  **What is Transcoding?**
    *   The process of converting a video file from one format/resolution to another.
2.  **What is HLS?**
    *   HTTP Live Streaming. A protocol that breaks video into small HTTP file downloads, allowing bitrate switching.
3.  **Why use a DAG (Directed Acyclic Graph) for transcoding?**
    *   To parallelize tasks. Step 1: Split video. Step 2 (Parallel): Encode chunks. Step 3: Merge.
