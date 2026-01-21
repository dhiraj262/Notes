# Day 49: Design Case - YouTube/Netflix

## 🎯 Goal
Design a video streaming platform that supports uploading, processing, and viewing videos at scale.
**Focus**: CDN, Transcoding, and Adaptive Bitrate Streaming.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload raw video files.
2.  **View**: Smooth playback on any device (Mobile, TV, Web).
3.  **Search/Feed**: Find videos.
4.  **Stats**: View counts, Likes.

### Non-Functional
1.  **Low Latency**: Start playing immediately (Buffering is bad).
2.  **Scalability**: Handle viral videos (Justin Bieber problem).
3.  **Availability**: 99.99%.
4.  **Cost**: Minimize bandwidth and storage costs.

---

## 📐 Capacity Estimation
*   **Users**: 1 Billion DAU.
*   **Uploads**: 500 hours of video/min.
*   **Storage**:
    *   1 min = 50MB (Raw).
    *   Transcoded (1080p, 720p, 480p, 360p) = 100MB total.
    *   Total/day = Massive. Needs Tiered Storage (S3 Standard -> Glacier).
*   **Bandwidth**: The biggest cost. CDN offload is mandatory.

---

## 🧠 Core Design Decisions

### 1. Protocol: UDP vs TCP vs HTTP
*   **UDP**: Fast but unreliable (pixelated frames). Good for Live calls (Zoom).
*   **HTTP (TCP)**: Reliable. Firewalls allow it.
*   **Adaptive Streaming (HLS/DASH)**:
    *   Video broken into 10-second chunks (`.ts` files).
    *   Manifest file (`.m3u8`) lists chunks for different qualities.
    *   Player detects bandwidth and requests appropriate chunk (360p if slow, 1080p if fast).

### 2. Storage: Blob Store + CDN
*   **Metadata** (Title, Description) -> **SQL/NoSQL** (Sharded).
*   **Video Files** -> **Blob Storage** (S3/GCS).
*   **Delivery** -> **CDN** (Cloudfront/Akamai). Edge servers cache popular content close to user.

### 3. Processing: Transcoding
*   Raw video (AVI/MOV) is huge and not web-friendly.
*   Must convert to MP4 (H.264/H.265) in various resolutions.
*   **DAG Model**: Split video -> Process chunks in parallel -> Merge.

---

## 🏗️ System Architecture

1.  **Upload Service**: Generates **Presigned URL**. Client uploads directly to **Original Storage (S3)**.
2.  **Transcoding Service**:
    *   Triggered by upload.
    *   Puts job in **Kafka**.
    *   **Workers** pull job, run `ffmpeg`.
    *   Generates chunks and manifest.
    *   Saves to **Transcoded Storage (S3)**.
3.  **CDN**: Pulls from Transcoded Storage on first request. caches it.
4.  **Streaming Service**: Client requests video ID. Returns URL to CDN manifest.

---

## 💻 Code Simulation: Transcoding Job Queue

```python
import time
import queue
import threading

class VideoTranscoder:
    def __init__(self):
        self.job_queue = queue.Queue()
        self.output_storage = {}

    def upload_video(self, video_id, raw_data):
        print(f"⬆️ Uploaded {video_id} (Raw). Queuing for transcoding...")
        self.job_queue.put(video_id)

    def worker(self):
        while True:
            try:
                vid = self.job_queue.get(timeout=2)
                self.process(vid)
                self.job_queue.task_done()
            except queue.Empty:
                break

    def process(self, vid):
        print(f"⚙️ Transcoding {vid}...")
        resolutions = ["360p", "720p", "1080p"]
        self.output_storage[vid] = []

        # Simulate CPU work
        time.sleep(1)

        for res in resolutions:
            chunk = f"{vid}_{res}.ts"
            self.output_storage[vid].append(chunk)
            print(f"   ✅ Generated {chunk}")

if __name__ == "__main__":
    system = VideoTranscoder()

    # Start workers
    t = threading.Thread(target=system.worker)
    t.start()

    # Users upload
    system.upload_video("vid_001", "raw_bytes")
    system.upload_video("vid_002", "raw_bytes")

    t.join()
    print("All jobs done.")
```

---

## 🧠 Interview Nuances

### 1. Safety?
*   **Signed URLs**: Don't make S3 bucket public. Generate a URL with signature valid for 1 hour. Give to client.
*   **DRM (Digital Rights Management)**: Encrypt chunks. Player needs a license key to decrypt (Widevine/FairPlay).

### 2. Deduplication?
*   User uploads same movie twice. Calculate hash (MD5) of file. If exists, point to existing file.

### 3. Latency vs Cost?
*   Cache popular videos (Top 20%) in CDN.
*   Long-tail videos (Bottom 80%) fetch from Origin S3 (Slower but cheaper).

---

## ⚡ Flashcards
1.  **What is HLS?**
    *   HTTP Live Streaming. Protocol by Apple. Breaks video into small HTTP file downloads.
2.  **Why use Pre-signed URLs?**
    *   Offloads traffic from your server. Client uploads directly to Cloud Storage (S3), which scales infinitely.
3.  **What is a CDN Edge Server?**
    *   A server physically close to the user (ISP level) that caches content to reduce latency.
