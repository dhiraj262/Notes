# Day 49: Design Youtube/Netflix

## 🎯 Goal
Design a video streaming platform.
**Focus**: Latency, Bandwidth Optimization (CDN), and Encoding.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload video (e.g., `.mov`).
2.  **View**: Users stream video (Adaptive Quality).
3.  **Search**: Find videos by title.
4.  **Interaction**: Likes, Comments.

### Non-Functional
1.  **Buffering**: Must be near zero.
2.  **Availability**: 99.99%.
3.  **Storage**: Massive. (Petabytes/Exabytes).

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million.
*   **Uploads**: 1 video/sec globally? No, Youtube gets 500 hours of video *every minute*.
*   **Storage**: 500 hours/min * 50MB/hour (compressed) = 25GB/min -> 36TB/day.
*   **Bandwidth**: The biggest cost.

---

## 🧠 Core Design Decisions

### 1. Transcoding / Encoding
*   Raw video is huge. We must compress it.
*   **Formats**: Support multiple formats (MP4, WebM) and codecs (H.264, VP9).
*   **Resolutions**: Generate 360p, 720p, 1080p, 4K versions for every upload.
*   **Technique**: **DAG (Directed Acyclic Graph)** model.
    *   Step 1: Validate.
    *   Step 2: Extract Audio.
    *   Step 3: Split into Chunks.
    *   Step 4: Encode Chunks in parallel.
    *   Step 5: Merge.

### 2. Adaptive Bitrate Streaming (ABR)
*   **Problem**: User's internet speed fluctuates.
*   **Solution**: **MPEG-DASH** or **HLS (HTTP Live Streaming)**.
    *   Break video into small chunks (e.g., 4 seconds).
    *   Encode each chunk in multiple qualities.
    *   Client Player detects bandwidth and requests the appropriate chunk (e.g., 4s of 4K, then internet drops, next 4s is 360p).

### 3. CDN (Content Delivery Network)
*   Serve video from a server close to the user (Edge Server).
*   **Netflix Open Connect**: Netflix places their own hardware ISP data centers to save bandwidth costs.

---

## 🏗️ System Architecture

1.  **Upload Service**: Presigned URL to S3.
2.  **S3 (Original Storage)**: Stores raw video.
3.  **Transcoding Service**:
    *   Triggered by upload.
    *   Uses **Workers** to process video.
    *   Saves `manifest.mpd` (Playlist) and chunks (`chunk_01_720p.mp4`) to S3.
4.  **CDN**: Caches chunks from S3.
5.  **Client Player**: Fetches `manifest.mpd`, then fetches chunks from CDN.

---

## 💻 Code Simulation: Adaptive Bitrate Logic

Simulating how the Client Player decides which quality to download next.

```python
class AdaptiveBitrate:
    def __init__(self, available_bandwidth):
        # Maps quality label to required bitrate (kbps)
        self.profiles = {
            "240p": 500,
            "480p": 1000,
            "720p": 2500,
            "1080p": 5000,
            "4K": 15000
        }
        self.bandwidth = available_bandwidth # kbps

    def get_best_quality(self):
        # Logic: Pick highest quality that uses < 80% of bandwidth (Safety buffer)
        safe_bandwidth = self.bandwidth * 0.8

        # Sort profiles by bitrate (ascending)
        sorted_profiles = sorted(self.profiles.items(), key=lambda x: x[1])

        best_quality = sorted_profiles[0][0] # Default to lowest

        for quality, bitrate in sorted_profiles:
            if bitrate <= safe_bandwidth:
                best_quality = quality
            else:
                break
        return best_quality

if __name__ == "__main__":
    # Scenario 1: Slow 3G
    net = AdaptiveBitrate(available_bandwidth=800)
    print(f"Internet: 800 kbps -> Stream: {net.get_best_quality()}")

    # Scenario 2: Fast 4G
    net = AdaptiveBitrate(available_bandwidth=4000)
    print(f"Internet: 4000 kbps -> Stream: {net.get_best_quality()}")

    # Scenario 3: Fiber
    net = AdaptiveBitrate(available_bandwidth=50000)
    print(f"Internet: 50000 kbps -> Stream: {net.get_best_quality()}")
```

---

## 🧠 Interview Nuances

### 1. How to secure paid content (Netflix)?
*   **DRM (Digital Rights Management)**. Encrypt the video chunks.
*   **Signed URLs**: The CDN URL is valid only for a specific IP and time. `cdn.netflix.com/movie.mp4?token=xyz&expiry=123`.

### 2. Deduplication?
*   If User A uploads "Movie.mp4" and User B uploads the exact same file.
*   Check Hash (MD5) before upload. If exists, just point User B to existing file.

### 3. Thumbnails?
*   Generate sprite sheets (one image containing 100 thumbnails) to reduce HTTP requests when scrubbing the seek bar.

---

## ⚡ Flashcards
1.  **What is Transcoding?**
    *   Converting a video file from one format/resolution to another (e.g., Raw MOV -> Optimized MP4 720p).
2.  **Push vs Pull CDN?**
    *   **Push**: You upload explicitly to CDN (good for small static sites).
    *   **Pull**: CDN fetches from Origin (S3) upon first user request (good for massive libraries like Netflix).
3.  **Why split video into chunks?**
    *   Allows switching quality mid-stream (ABR). Allows parallel downloading.
