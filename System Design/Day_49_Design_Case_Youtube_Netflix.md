# Day 49: Design Case - YouTube/Netflix

## 🎯 Goal
Design a video sharing/streaming platform.
**Focus**: Large Scale Blob Storage, CDN, and Adaptive Streaming.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload videos.
2.  **View**: Users stream videos.
3.  **Search**: Find videos by title.
4.  **Stats**: View count, Likes.

### Non-Functional
1.  **Buffering**: Must be minimal.
2.  **Availability**: High.
3.  **Latency**: Start playing within 200ms.

---

## 📐 Capacity Estimation
*   **DAU**: 1 Billion.
*   **Uploads**: 500 hours of video/minute.
*   **Storage**: Huge! (Exabytes).
*   **Bandwidth**: Critical.

---

## 🏗️ System Architecture

### 1. Upload Flow
1.  User uploads `raw.mp4` to **Original Storage (S3)**.
2.  **Transcoding Service** (Workers):
    *   Converts raw file into multiple formats (MP4, WEBM) and resolutions (360p, 720p, 4k).
    *   Splits video into small chunks (e.g., 5-second segments) for streaming.
    *   Technique: **DAG (Directed Acyclic Graph)** workflow manager (like Airflow) for encoding steps.

### 2. Streaming (CDN)
*   **Adaptive Bitrate Streaming (MPEG-DASH / HLS)**.
*   Client detects bandwidth.
*   If slow, request `chunk_1_360p.ts`.
*   If fast, request `chunk_2_1080p.ts`.
*   Content is served from **CDN (Cloudfront/Akamai)** close to the user.

### 3. Database
*   **Video Metadata**: MySQL/Postgres (Video Title, Uploader ID).
*   **User Data**: NoSQL (Cassandra) for Watch History.
*   **Counts**: Redis for fast increment, flush to DB periodically.

---

## 💻 Code Simulation: Adaptive Bitrate Logic

Simulating how a server might organize files and how a client selects quality.

```python
class VideoService:
    def __init__(self):
        self.cdn = {} # url -> content

    def upload(self, video_id, raw_file):
        print(f"🎬 Uploading {video_id}...")

        # 1. Transcoding
        formats = ["360p", "720p", "1080p"]
        for fmt in formats:
            self.transcode(video_id, raw_file, fmt)

    def transcode(self, video_id, file, quality):
        print(f"   ⚙️ Transcoding to {quality}...")
        # 2. Upload to CDN
        url = f"cdn.com/{video_id}/{quality}.mp4"
        self.cdn[url] = f"{file} [{quality}]"
        print(f"   ☁️ Uploaded to CDN: {url}")

    def stream(self, video_id, bandwidth):
        # 3. Adaptive Bitrate
        quality = "360p"
        if bandwidth > 5: quality = "1080p"
        elif bandwidth > 2: quality = "720p"

        url = f"cdn.com/{video_id}/{quality}.mp4"
        print(f"📺 Streaming from: {url}")

if __name__ == "__main__":
    youtube = VideoService()
    youtube.upload("vid_123", "RawData")

    print("\n-- Client (Slow Internet) --")
    youtube.stream("vid_123", bandwidth=1.5) # Mbps

    print("\n-- Client (Fast Internet) --")
    youtube.stream("vid_123", bandwidth=10.0)
```

**Output:**
```
🎬 Uploading vid_123...
   ⚙️ Transcoding to 360p...
   ☁️ Uploaded to CDN: cdn.com/vid_123/360p.mp4
   ⚙️ Transcoding to 720p...
   ☁️ Uploaded to CDN: cdn.com/vid_123/720p.mp4
   ⚙️ Transcoding to 1080p...
   ☁️ Uploaded to CDN: cdn.com/vid_123/1080p.mp4

-- Client (Slow Internet) --
📺 Streaming from: cdn.com/vid_123/360p.mp4

-- Client (Fast Internet) --
📺 Streaming from: cdn.com/vid_123/1080p.mp4
```

---

## 🧠 Interview Nuances

### 1. Master-Slave Architecture for Video Processing
*   The upload isn't one monolithic process.
*   Split video -> Process audio -> Process video -> Merge.
*   Parallelize using queues.

### 2. CDN Costs
*   CDN is the most expensive part.
*   **Optimization**: Don't cache unpopular videos at the edge. Serve from S3 (Origin) directly for long-tail content.

### 3. DRM (Digital Rights Management)
*   Netflix needs this. Encrypt chunks. Client needs a license key to decrypt.

---

## ⚡ Flashcards
1.  **What is Transcoding?**
    *   Converting a video file from one format/resolution to another to support different devices and bandwidths.
2.  **What is HLS?**
    *   HTTP Live Streaming. Breaks video into small files (`.ts`) and uses a manifest file (`.m3u8`) to tell the player which file to play next.
3.  **Edge vs Origin?**
    *   Origin: Where the file is permanently stored (S3).
    *   Edge: A CDN server close to the user that caches the file.
