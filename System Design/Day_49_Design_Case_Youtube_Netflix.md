# Day 49: Design Case - Video Streaming (YouTube/Netflix)

## 🎯 Goal
Design a global video streaming platform capable of handling upload, processing, and playback of petabytes of video data.
**Focus**: Latency, Throughput (Bandwidth), and Reliability.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload videos (up to 4K).
2.  **Playback**: Adaptive streaming (quality changes based on network).
3.  **Search**: Find videos by title/tag.
4.  **Interaction**: Likes, Comments (Eventual consistency).

### Non-Functional
1.  **Low Latency**: Start playing immediately (Buffering < 200ms).
2.  **Scalability**: Support millions of concurrent viewers for a popular video.
3.  **Availability**: 99.99%.

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million.
*   **Uploads**: 500 hours/minute.
    *   1 min video ≈ 50MB (Raw). 500 hours * 60 * 50MB ≈ 1.5 TB/min -> 2 PB/day.
*   **Bandwidth**: Reading is heavy. 100M users * 10 mins * 10MB/min = 10 PB/day egress.

---

## 🧠 Core Design Decisions

### 1. Storage: Blob vs Block
*   Videos are large immutable blobs.
*   **Use Object Storage (S3/GCS)**. Cheap, durable.
*   Metadata (Title, Author) goes to **SQL/NoSQL** (Spanner/Cassandra).

### 2. Processing: Transcoding (Encoding)
*   Raw video is huge and singular format.
*   Need to convert to:
    *   **Containers**: .mp4, .avi, .mkv
    *   **Codecs**: H.264, VP9, AV1.
    *   **Resolutions**: 360p, 720p, 1080p, 4K.
*   **DAG Workflow**: Split video -> Process chunks in parallel -> Merge.

### 3. Delivery: CDN & Adaptive Bitrate
*   **CDN**: Cache popular content at the edge (ISP level). Netflix Open Connect.
*   **Adaptive Bitrate (ABR)**: Client detects bandwidth.
    *   Fast net -> Request 1080p chunk.
    *   Slow net -> Request 360p chunk.
    *   Protocols: **HLS** (Apple), **MPEG-DASH**.

---

## 🏗️ System Architecture

1.  **Upload Service**: Receives video, saves to temp S3.
2.  **Encoding Service**:
    *   Split video into 5-min chunks.
    *   Workers transcode chunks to various formats.
    *   Save processed chunks to S3 (Origin).
3.  **CDN**: Pulls from S3.
4.  **Metadata DB**: Stores URL of the manifest file.
5.  **Client**:
    *   Fetches `master.m3u8` (Manifest).
    *   Decides quality.
    *   Downloads chunks from CDN.

---

## 💻 Code Simulation: Transcoding & Manifest

Simulating the logic of breaking a video into chunks and generating an HLS manifest.

```python
class VideoTranscoder:
    def __init__(self, video_id, duration):
        self.video_id = video_id
        self.duration = duration
        self.resolutions = ["360p", "720p", "1080p"]
        self.chunks = []

    def transcode_and_chunk(self):
        print(f"🎬 Processing Video: {self.video_id} ({self.duration}s)")

        # Simulate creating a master manifest file (HLS .m3u8)
        manifest = f"#EXTM3U\n#EXT-X-VERSION:3\n"

        for res in self.resolutions:
            print(f"   ⚙️ Transcoding to {res}...")
            # Create 10-second chunks
            for i in range(0, self.duration, 10):
                chunk_name = f"{self.video_id}_{res}_{i}.ts"
                self.chunks.append(chunk_name)
                print(f"      🔹 Created Chunk: {chunk_name}")

            manifest += f"#EXT-X-STREAM-INF:BANDWIDTH=...,RESOLUTION={res}\n{self.video_id}_{res}.m3u8\n"

        return manifest

    def get_cdn_url(self, chunk_name):
        # Simulate Signed URL generation for security
        return f"https://cdn.netflix.com/{chunk_name}?token=xyz123"

if __name__ == "__main__":
    transcoder = VideoTranscoder("video_123", duration=30) # 30 seconds
    manifest_content = transcoder.transcode_and_chunk()

    print("\n📜 Generated Master Manifest:")
    print(manifest_content)

    print("\n🌍 CDN Access:")
    print(transcoder.get_cdn_url("video_123_1080p_10.ts"))
```

**Output:**
```
🎬 Processing Video: video_123 (30s)
   ⚙️ Transcoding to 360p...
      🔹 Created Chunk: video_123_360p_0.ts
      🔹 Created Chunk: video_123_360p_10.ts
      🔹 Created Chunk: video_123_360p_20.ts
   ⚙️ Transcoding to 720p...
      🔹 Created Chunk: video_123_720p_0.ts
      🔹 Created Chunk: video_123_720p_10.ts
      🔹 Created Chunk: video_123_720p_20.ts
   ⚙️ Transcoding to 1080p...
      🔹 Created Chunk: video_123_1080p_0.ts
      🔹 Created Chunk: video_123_1080p_10.ts
      🔹 Created Chunk: video_123_1080p_20.ts

📜 Generated Master Manifest:
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=...,RESOLUTION=360p
video_123_360p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=...,RESOLUTION=720p
video_123_720p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=...,RESOLUTION=1080p
video_123_1080p.m3u8

🌍 CDN Access:
https://cdn.netflix.com/video_123_1080p_10.ts?token=xyz123
```

---

## 🧠 Interview Nuances

### 1. How to secure paid content?
*   **Signed URLs**: The URL contains a temporary token/signature valid for X minutes.
*   **DRM (Digital Rights Management)**: Encrypt the actual video stream (Widevine, FairPlay). Key exchange needed.

### 2. How to handle "Celebrity" uploads?
*   If Justin Bieber uploads a video, millions view it instantly.
*   **Thundering Herd**: CDN Cache miss can crash Origin.
*   **Solution**: Pre-warm the CDN (Push content to Edge before publishing).

### 3. Deduplication?
*   Analyze video hash (fingerprint) to stop unauthorized re-uploads of copyrighted content.

---

## ⚡ Flashcards
1.  **What is Adaptive Bitrate Streaming?**
    *   A technique where the video quality automatically adjusts based on the user's internet speed and device capabilities.
2.  **Why use a CDN for video?**
    *   Significantly reduces latency by serving content from a server geographically close to the user, and reduces load on the origin server.
3.  **What is Transcoding?**
    *   The process of converting a video file from one format (and resolution) to another, to ensure compatibility with different devices.
