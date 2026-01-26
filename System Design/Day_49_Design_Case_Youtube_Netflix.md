# Day 49: Design Case - Youtube/Netflix (Video Streaming)

## 🎯 Goal
Design a video streaming platform where users can upload, view, and share videos.
**Focus**: Large File Handling, Transcoding, CDNs, and Adaptive Streaming.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload video files (MOV, MP4, AVI).
2.  **View**: Users watch videos (smooth streaming, no buffering).
3.  **Search**: Users can search by title.
4.  **Stats**: View count, Likes.

### Non-Functional
1.  **High Availability**: Videos must always be playable.
2.  **Scalability**: Support viral videos (Justin Bieber effect).
3.  **Performance**: Low latency start time.
4.  **Reliability**: No lost uploads.

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million.
*   **Uploads**: 1 video/user/year -> 300k videos/day.
*   **Views**: 5 videos/user/day -> 500 Million views/day.
*   **Storage**:
    *   Avg video size: 500MB (Source). Transcoded versions: 1GB total.
    *   Daily: 300k * 1GB = 300 TB/day.
    *   Bandwidth: Massive. CDN is mandatory.

---

## 🧠 Core Design Decisions

### 1. Protocols: UDP vs TCP vs HTTP
*   **UDP**: Fast but loses packets (glitches). Good for live calls (Zoom), bad for Movies.
*   **TCP**: Reliable but slow (head-of-line blocking).
*   **HTTP (DASH/HLS)**: **Winner**.
    *   Videos are chunked into small segments (2-10 seconds).
    *   Client downloads chunks via HTTP.
    *   Firewall friendly. CDN friendly.

### 2. Adaptive Bitrate Streaming (ABR)
*   **Problem**: Users have different internet speeds (4G, 5G, Fiber).
*   **Solution**: Transcode original video into multiple resolutions (360p, 720p, 1080p, 4K) and bitrates.
*   Client automatically switches quality based on bandwidth.

### 3. Storage: BLOB + CDN
*   **Original File**: Store in AWS S3 (Glacier for backup).
*   **Transcoded Files**: Store in S3 (Standard).
*   **Delivery**: Push popular content to CDNs (Cloudfront/Akamai) at the edge.

---

## 🏗️ System Architecture

### Upload Path
1.  **User** uploads video to `Original Storage` (S3) via Signed URL.
2.  **Upload Service** updates Metadata DB (Processing status = "Pending").
3.  **Transcoding Service** (Worker Cluster):
    *   Pulls video from S3.
    *   Splits into chunks.
    *   Encodes to mp4, webm, hls.
    *   Generates Thumbnail.
4.  **Completion**: Updates DB (Status = "Ready"). Pushes to CDN.

### Viewing Path
1.  **User** requests video page.
2.  **Web Server** returns Metadata (Title, Description) + **Manifest File URL**.
3.  **Client Player** reads Manifest (list of .ts chunks for different qualities).
4.  **Client** downloads chunks from nearest **CDN**.
5.  **Client** adapts quality dynamically.

---

## 💻 Code Simulation: Adaptive Bitrate Selector

Simulating the client-side logic that chooses the next chunk quality based on bandwidth.

```python
import random
import time

class VideoPlayer:
    def __init__(self):
        # Available bitrates in kbps
        self.qualities = {
            "360p": 500,
            "720p": 1500,
            "1080p": 4000,
            "4K": 12000
        }
        self.buffer = 0 # seconds of video buffered

    def estimate_bandwidth(self):
        # Simulate fluctuating network (kbps)
        return random.randint(300, 8000)

    def select_quality(self, bandwidth):
        # Conservative approach: Use 80% of bandwidth
        safe_bandwidth = bandwidth * 0.8

        selected = "360p" # Default fallback
        for quality, bitrate in sorted(self.qualities.items(), key=lambda x: x[1]):
            if bitrate <= safe_bandwidth:
                selected = quality
            else:
                break
        return selected

    def download_chunk(self):
        bw = self.estimate_bandwidth()
        quality = self.select_quality(bw)
        print(f"📡 Network: {bw} kbps | Choosing: {quality}")

        # Simulate download
        time.sleep(0.5)
        self.buffer += 4 # Add 4 seconds to buffer

    def play(self):
        for i in range(5):
            self.download_chunk()
            print(f"   ▶️ Playing... Buffer: {self.buffer}s")
            self.buffer -= 2 # Consume 2 seconds
            if self.buffer < 0:
                print("   ⚠️ Buffering...")
                self.buffer = 0

if __name__ == "__main__":
    player = VideoPlayer()
    player.play()
```

**Output:**
```
📡 Network: 7200 kbps | Choosing: 1080p
   ▶️ Playing... Buffer: 4s
📡 Network: 1200 kbps | Choosing: 360p
   ▶️ Playing... Buffer: 6s
📡 Network: 4500 kbps | Choosing: 1080p
   ▶️ Playing... Buffer: 8s
...
```

---

## 🧠 Interview Nuances

### 1. How to optimize storage costs?
*   **Deduplication**: Check hash of uploaded file.
*   **Cold Storage**: Move unpopular videos to S3 Glacier (cheaper, slower access) after 6 months.
*   **Codec Efficiency**: Use HEVC (H.265) or AV1 to save 30% bandwidth over H.264.

### 2. Directed Acyclic Graph (DAG) for Transcoding
*   Video processing is a pipeline: `Upload -> Split -> [Audio Extract, Video Resize, Thumbnail] -> Merge`.
*   Facebook/Netflix manage this using a DAG scheduler to parallelize tasks.

### 3. DRM (Digital Rights Management)
*   Need to encrypt chunks so users can't just download and resell Netflix movies.
*   Use Widevine/FairPlay.

---

## ⚡ Flashcards
1.  **What is a CDN?**
    *   Content Delivery Network. A network of servers distributed geographically to deliver content (videos, images) from the location closest to the user.
2.  **What is HLS?**
    *   HTTP Live Streaming. An ABR protocol developed by Apple. Splits video into `.ts` files and uses a `.m3u8` playlist.
3.  **Why split videos into chunks?**
    *   Allows fast seeking (jump to 50:00 without downloading 0-49:00). Allows switching quality mid-stream.
