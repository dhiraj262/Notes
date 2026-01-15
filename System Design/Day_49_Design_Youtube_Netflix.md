# Day 49: Design Youtube/Netflix

## 🎯 Goal
Design a video streaming platform.
**Focus**: Large Object Storage, Transcoding (DAG), CDN, and Adaptive Bitrate Streaming.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload raw video.
2.  **View**: Users stream video (no buffering).
3.  **Search**: Find videos by title.
4.  **Analytics**: View count, watch time.

### Non-Functional
1.  **Reliability**: Uploads must not fail midway.
2.  **Availability**: Playback must always work (CDN).
3.  **Scalability**: Handle popular videos (Justin Bieber case).

---

## 📐 Capacity Estimation
*   **DAU**: 1 Billion Users.
*   **Uploads**: 500 hours of video / minute.
*   **Storage**: 1 min video = 50MB (HQ).
    *   Daily: 500 * 60 * 24 * 50MB = 36 PB / day? (Needs heavy compression/dedup, or numbers are for raw).
*   **Bandwidth**: Main cost driver.

---

## 🧠 Core Design Decisions

### 1. Adaptive Bitrate Streaming (ABS)
*   **Problem**: User on 3G cannot stream 4K.
*   **Solution**: **MPEG-DASH / HLS (Apple)**.
    *   Break video into 4-second chunks.
    *   Encode each chunk in multiple bitrates (360p, 720p, 1080p).
    *   Player detects bandwidth and requests appropriate chunk `video_1080p_001.ts`.

### 2. Transcoding Pipeline (DAG)
*   Raw video is huge. Must convert to mp4/webm + different resolutions.
*   Use a **DAG (Directed Acyclic Graph)** model.
    *   Split video -> Process Audio -> Process Video (Parallel) -> Merge.

### 3. CDN (Content Delivery Network)
*   Store popular videos in Edge Servers (ISP Data Centers).
*   **Long-tail videos** stay in S3 (Origin).

---

## 🏗️ System Architecture

1.  **Upload Service**:
    *   Presigned URL to S3 (Direct upload).
2.  **Transcoding Cluster**:
    *   Workers pick up "New Upload" event.
    *   Run ffmpeg jobs.
    *   Store artifacts in S3 + CDN.
3.  **Metadata DB**:
    *   MySQL/Postgres (Sharded). Stores `VideoID`, `Title`, `UploaderID`.
4.  **Streaming Service**:
    *   Returns the **Manifest File** (`.m3u8` or `.mpd`) listing chunk URLs.

---

## 💻 Code Simulation: Transcoding Mock

Simulating the workflow of converting raw video into multiple formats.

```python
import time

class VideoTranscoder:
    def __init__(self):
        self.queue = []

    def upload(self, video_id, raw_file):
        print(f"⬆️ Uploaded {video_id} ({len(raw_file)} bytes).")
        self.queue.append(video_id)
        self.process_queue()

    def process_queue(self):
        while self.queue:
            vid = self.queue.pop(0)
            self.transcode(vid)

    def transcode(self, video_id):
        print(f"🎬 Processing {video_id}...")
        resolutions = ["1080p", "720p", "480p"]
        formats = ["mp4", "webm"]

        # Simulating DAG (Directed Acyclic Graph) of tasks
        for res in resolutions:
            for fmt in formats:
                self.convert_chunk(video_id, res, fmt)

        print(f"✅ {video_id} Ready for streaming.\n")

    def convert_chunk(self, vid, res, fmt):
        # Simulation of heavy compute
        print(f"   ⚙️ Converting chunk -> {res} / {fmt}")

if __name__ == "__main__":
    youtube = VideoTranscoder()
    youtube.upload("Video_A", b"raw_data_1GB")
    youtube.upload("Video_B", b"raw_data_500MB")
```

**Output:**
```
⬆️ Uploaded Video_A (12 bytes).
🎬 Processing Video_A...
   ⚙️ Converting chunk -> 1080p / mp4
   ...
✅ Video_A Ready for streaming.
```

---

## 🧠 Interview Nuances

### 1. How to optimize storage?
*   **Deduplication**: If 100 people upload the same movie, store once.
*   **Cold Storage**: Move videos with 0 views in 1 year to Glacier.

### 2. Encryption (DRM)?
*   **Widevine / FairPlay**. Encrypt chunks. Player gets key from license server.

### 3. Thumbnails?
*   Generate Sprite Sheet (Big image with many small thumbnails) to reduce HTTP requests when scrubbing the seek bar.

---

## ⚡ Flashcards
1.  **What is a Manifest File (M3U8)?**
    *   A text file that acts as a playlist, telling the player where to find the chunks for different bitrates.
2.  **Presigned URL?**
    *   A way to let a user upload directly to S3 without the data passing through your API server (saving bandwidth).
3.  **Why use UDP (QUIC) for streaming?**
    *   TCP retransmission causes buffering (Head-of-Line blocking). QUIC/UDP is faster for real-time.
