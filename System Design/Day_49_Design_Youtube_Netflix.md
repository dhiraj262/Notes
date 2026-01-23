# Day 49: Design Youtube/Netflix

## 🎯 Goal
Design a global video sharing and streaming platform like YouTube or Netflix.
**Focus**: Upload flow, Transcoding (DAG model), Adaptive Bitrate Streaming, and CDN distribution.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload video files (MP4, MKV).
2.  **Streaming**: Users watch videos buffer-free.
3.  **Search**: Find videos by title.
4.  **Recommendations**: "Up Next".

### Non-Functional
1.  **High Availability**: Videos always playable.
2.  **Low Latency**: Fast start time.
3.  **Scalability**: Handle popular viral videos.

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million.
*   **Uploads**: 1 video/user/month -> 3M uploads/day.
*   **Storage**: 3M * 500MB = 1.5 PB/day. (Massive storage).
*   **Bandwidth**: Streaming dominates cost. CDN is mandatory.

---

## 🧠 Core Design Decisions

### 1. Adaptive Bitrate Streaming (ABS)
*   **Problem**: Users have different internet speeds (3G vs 5G vs Fiber).
*   **Solution**: Create multiple versions of the same video (360p, 720p, 1080p, 4K).
*   **Protocol**: HLS (HTTP Live Streaming) or DASH.
*   Video is broken into small "chunks" (ts files). Player switches quality based on bandwidth.

### 2. Transcoding Pipeline (DAG)
*   Video processing is heavy. Can't be monolithic.
*   **DAG (Directed Acyclic Graph)**:
    *   Step 1: Check metadata.
    *   Step 2: Split into chunks.
    *   Step 3: Transcode chunks in parallel (Audio, Video 360p, Video 720p).
    *   Step 4: Merge/Manifest generation.

### 3. Content Delivery Network (CDN)
*   Serve video from the edge server closest to the user.
*   **Caching Policy**:
    *   **Hot Videos**: Cache in all Edge locations.
    *   **Cold Videos**: Fetch from Origin (S3) on demand.

---

## 🏗️ System Architecture

1.  **Upload Service**: Pre-signed URL to S3 (Direct upload).
2.  **S3 (Original Storage)**: Stores raw video.
3.  **Transcoding Service**:
    *   Triggered by upload.
    *   Breaks video into chunks.
    *   Converts to HLS/DASH formats.
    *   Saves processed chunks to S3.
4.  **CDN**: Pulls processed chunks from S3 and caches them globally.
5.  **Client**: Downloads "Manifest file" (.m3u8), then requests chunks from CDN.

---

## 💻 Code Simulation: Transcoding Job

Simulating the breaking down of a video job into parallel tasks.

```python
import time
import concurrent.futures

class VideoTranscoder:
    def __init__(self):
        self.resolutions = ["360p", "720p", "1080p"]

    def process_video(self, video_id):
        print(f"🎬 Received Video {video_id}. Starting Pipeline...")

        # Step 1: Validation
        self.validate(video_id)

        # Step 2: Parallel Transcoding
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.transcode_chunk, video_id, res) for res in self.resolutions]
            for f in concurrent.futures.as_completed(futures):
                print(f"   ✅ {f.result()}")

        # Step 3: Manifest Generation
        self.generate_manifest(video_id)
        print(f"🎉 Video {video_id} Ready for Streaming!")

    def validate(self, vid):
        print("   🔍 Validating format... OK.")
        time.sleep(0.5)

    def transcode_chunk(self, vid, res):
        time.sleep(1) # Simulate heavy work
        return f"Chunk {res} Transcoded"

    def generate_manifest(self, vid):
        print("   📄 Generating HLS Manifest (.m3u8)...")

if __name__ == "__main__":
    youtube = VideoTranscoder()
    youtube.process_video("vid_101")
```

**Output:**
```
🎬 Received Video vid_101. Starting Pipeline...
   🔍 Validating format... OK.
   ✅ Chunk 720p Transcoded
   ✅ Chunk 360p Transcoded
   ✅ Chunk 1080p Transcoded
   📄 Generating HLS Manifest (.m3u8)...
🎉 Video vid_101 Ready for Streaming!
```

---

## 🧠 Interview Nuances

### 1. Safety & Copyright?
*   Compute hash of uploaded video. Check against "Copyright Database" (Content ID).
*   AI Model to detect NSFW content during the validation step.

### 2. Optimizing Storage?
*   Use different compression algorithms.
*   **Cold Storage**: Move videos with 0 views in 1 year to Amazon Glacier (Cheaper, slower access).

### 3. How to handle "Viral" spikes?
*   The CDN handles the read traffic. The challenge is the "Thundering Herd" on the cache miss.
*   **Request Collapsing**: If 10,000 users ask for `chunk_1.ts` and it's not in cache, CDN should send **only one** request to Origin, then serve all 10,000.

---

## ⚡ Flashcards
1.  **What is Adaptive Bitrate Streaming?**
    *   A technique where video quality dynamically adjusts based on the user's real-time network speed (e.g., dropping from 1080p to 480p if bandwidth drops).
2.  **Why use Pre-signed URLs for upload?**
    *   To allow the client to upload directly to S3 (Object Storage) without burdening the application servers with heavy file data.
3.  **What is a CDN Edge Server?**
    *   A server geographically close to the user that caches static content (images, video chunks) to reduce latency and load on the origin server.
