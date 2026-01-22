# Day 49: Design Case - YouTube/Netflix (Video Streaming)

## 🎯 Goal
Design a video streaming platform that serves content to millions of concurrent users with low latency.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload videos (1GB - 50GB).
2.  **Transcoding**: Convert raw video to multiple formats/resolutions (480p, 720p, 1080p, 4K) and codecs (H.264, VP9).
3.  **Streaming**: Smooth playback, adaptive bitrate (auto-switch quality).
4.  **Metadata**: Title, Description, Likes.

### Non-Functional
1.  **High Availability**: Videos must always be playable.
2.  **Scalability**: Handle viral videos (millions of views/hour).
3.  **Latency**: Minimal buffering (Start time < 2s).

---

## 📐 Capacity Estimation
*   **DAU**: 1 Billion (YouTube scale).
*   **Uploads**: 500 hours of video/minute.
*   **Storage**: 500 hours * 60 min * 500MB = 15 PB/day. (Needs heavy compression and tiered storage).
*   **Bandwidth**: Massive. CDN is mandatory.

---

## 🧠 Core Design Decisions

### 1. Adaptive Bitrate Streaming (ABS)
*   **Problem**: Users have different internet speeds (3G vs Fiber). Sending 4K to a 3G phone causes buffering.
*   **Solution**: **HLS (HTTP Live Streaming)** or **MPEG-DASH**.
    *   Split video into small chunks (e.g., 5 seconds).
    *   Encode each chunk in multiple qualities (360p, 720p, 1080p).
    *   Client downloads chunks based on current bandwidth.

### 2. Video Upload & Transcoding Pipeline
*   Uploading a single large file is risky (network fail = restart).
*   **Solution**:
    *   Client uses **Pre-signed URL** to upload direct to Object Storage (S3).
    *   Upload triggers an event (S3 Event -> Lambda/Kafka).
    *   **Transcoding Service** (Worker Cluster) picks up the job.
    *   Break video into segments to transcode in parallel (DAG model).

### 3. Content Delivery Network (CDN)
*   You cannot serve 1B users from one data center.
*   **Strategy**: Cache popular videos (the "head") in CDNs (Edge locations close to user).
*   **Long Tail**: Less popular videos stay in S3 (Origin) or cold storage (Glacier).

---

## 🏗️ System Architecture

1.  **User** uploads `video.mp4` to S3 (via API Gateway presigned URL).
2.  **Upload Service** publishes message to `transcode-queue` (Kafka).
3.  **Transcoder Workers**:
    *   Download video.
    *   Split into chunks.
    *   Convert to 360p, 720p, 1080p.
    *   Upload chunks back to S3.
4.  **Metadata Service**: Updates DB (SQL/NoSQL) with `video_url`.
5.  **User (Viewer)**:
    *   Requests video.
    *   Client receives a **Manifest File** (`.m3u8`).
    *   Client logic: "Net is fast? Get 1080p chunk. Net dropped? Get 360p chunk."

---

## 💻 Code Simulation: Manifest Generation

Simulates the output of the Transcoding service: Chunking and Manifest creation.

```python
class VideoProcessor:
    def __init__(self, video_id, duration):
        self.video_id = video_id
        self.duration = duration
        self.chunks = []
        self.manifest = ""

    def chunk_video(self, chunk_size=5):
        print(f"🎬 Chunking Video {self.video_id} ({self.duration}s)...")
        for t in range(0, self.duration, chunk_size):
            end = min(t + chunk_size, self.duration)
            chunk_name = f"{self.video_id}_{t}_{end}.ts"
            self.chunks.append(chunk_name)
            print(f"   ✂️ Created chunk: {chunk_name}")

    def generate_manifest(self):
        print("\n📄 Generating HLS Manifest...")
        # Simple HLS format
        self.manifest = "#EXTM3U\n#EXT-X-VERSION:3\n"
        for chunk in self.chunks:
            self.manifest += f"#EXTINF:5.0,\n{chunk}\n"
        self.manifest += "#EXT-X-ENDLIST"
        print("✅ Manifest Created:")
        print(self.manifest)

# Simulation Usage
if __name__ == "__main__":
    # Simulate a 15 second video
    processor = VideoProcessor(video_id="vid_123", duration=15)

    # 1. Transcoding Step: Chunking
    processor.chunk_video(chunk_size=5)

    # 2. Transcoding Step: Create Index
    processor.generate_manifest()
```

---

## 🧠 Interview Nuances

### 1. Optimization: Pre-computation vs On-the-fly?
*   **Transcoding**: Always pre-compute. Too expensive to do on-the-fly.
*   **Packaging**: Can be done on-the-fly (Packaging raw H.264 into HLS/DASH container) to save storage.

### 2. DRM (Digital Rights Management)?
*   If building Netflix, you need Widevine/FairPlay.
*   Encrypt the video chunks. Key exchange required before playback.

### 3. How to deduplicate uploads?
*   User A and User B upload the same viral video.
*   Calculate Hash (SHA-256) of the file before upload. If exists, just link to existing S3 object.

---

## ⚡ Flashcards
1.  **What is a Manifest File?**
    *   A text file (like `.m3u8` or `.mpd`) that acts as a playlist. It tells the player where the video chunks are and what qualities are available.
2.  **What is Transcoding?**
    *   The process of converting a video file from one format/codec to another (e.g., AVI to MP4, 4K to 480p).
3.  **Why use Pre-signed URLs for upload?**
    *   To offload the bandwidth from your API servers. The client talks directly to the heavy storage layer (S3), which is designed for high throughput.
