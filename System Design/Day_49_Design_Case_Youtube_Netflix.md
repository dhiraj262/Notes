# Day 49: Design Case - Youtube / Netflix

## 🎯 Goal
Design a video streaming platform.
**Focus**: Blob Storage, CDN, Transcoding, and Adaptive Streaming.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users upload videos.
2.  **View**: Users stream videos.
3.  **Search**: Find videos by title.
4.  **Stats**: View count, likes.

### Non-Functional
1.  **Reliability**: No buffering (stuttering).
2.  **Availability**: Videos always available.
3.  **Scalability**: High throughput for popular videos.

---

## 📐 Capacity Estimation
*   **DAU**: 100M.
*   **Uploads**: 1 video/user/year? -> Heavy write load (GBs).
*   **Storage**: PetaBytes/Exabytes.
*   **Bandwidth**: The biggest cost and bottleneck.

---

## 🧠 Core Design Decisions

### 1. Storage: Blob Store + CDN
*   **Database**: Storing MP4 in MySQL is suicidal.
*   **Blob Store (S3/GCS)**: Stores the raw video file.
*   **CDN (Cloudfront/Akamai)**: Caches popular content at the "Edge" (close to user).
    *   *Optimization*: Only cache popular videos. Long-tail videos served from S3 directly (cheaper).

### 2. Transcoding (Encoding)
*   Raw video is huge. Users have different devices (Phone vs 4K TV) and bandwidth (3G vs Fiber).
*   **Transcoding**: Convert raw file into multiple formats (Codecs: H.264, VP9) and Resolutions (360p, 720p, 1080p).
*   **DAG (Directed Acyclic Graph)**: Pipeline the jobs.
    *   Upload -> Split Audio/Video -> Transcode 1080p -> Transcode 720p -> Merge -> Upload to S3.

### 3. Adaptive Bitrate Streaming (ABS)
*   **Protocols**: HLS (Apple), MPEG-DASH.
*   **Chunking**: Break video into 10-second chunks.
*   **Manifest File (.m3u8)**: Tells the player "Here are the chunks for 360p, here for 1080p".
*   Player auto-switches resolution based on internet speed.

---

## 🏗️ System Architecture

1.  **Upload Service**:
    *   Presigned URL (Direct upload to S3). Don't proxy 1GB through your API server.
2.  **Transcoding Service**:
    *   S3 Event -> Kafka -> Worker Group.
    *   ffmpeg runs to convert video.
    *   Save chunks back to S3.
3.  **CDN**:
    *   Pulls chunks from S3.
4.  **Streaming Service**:
    *   Returns the Manifest URL to the client.
    *   Client player handles the rest.

---

## 💻 Code Simulation: Smart CDN Selection

Mocking the logic of choosing the best edge server.

```python
class LoadBalancer:
    def __init__(self):
        # Mock CDN Edge Servers with latency map
        self.nodes = {
            "us-east": {"lat": 20, "load": 50},
            "us-west": {"lat": 150, "load": 20},
            "eu-central": {"lat": 200, "load": 10}
        }

    def get_best_node(self, user_region):
        print(f"🌍 User from {user_region} requesting video...")

        # Simple Logic: Pick lowest latency
        # (In reality: Balance Latency vs Load vs Cost)
        best_node = None
        min_score = float('inf')

        for name, stats in self.nodes.items():
            # Mock scoring: Latency + (Load * 0.5)
            # If load is high, latency matters less (shed load)
            score = stats['lat'] + (stats['load'] * 0.5)

            # Simulate "us-east" being close to user
            if user_region == "NY" and name == "us-east":
                score -= 10 # Boost

            print(f"   Server {name}: Score {score}")
            if score < min_score:
                min_score = score
                best_node = name

        return best_node

if __name__ == "__main__":
    lb = LoadBalancer()
    node = lb.get_best_node("NY")
    print(f"✅ Redirecting to: {node}")
```

**Output:**
```
🌍 User from NY requesting video...
   Server us-east: Score 35.0
   Server us-west: Score 160.0
   Server eu-central: Score 205.0
✅ Redirecting to: us-east
```

---

## 🧠 Interview Nuances

### 1. The "Popularity" Problem
*   Justin Bieber releases a song. 100M users hit CDN.
*   **Thundering Herd**: If CDN misses cache, 100M reqs hit S3.
*   **Fix**: Request Collapsing (CDN holds 999,999 reqs, fetches once, serves all).

### 2. Digital Rights Management (DRM)
*   Need to encrypt chunks so people don't download movies.
*   AES Encryption. Player needs a license key to decrypt.

### 3. Thumbnails
*   Generate Sprite Sheet (one big image with many small thumbnails) to save HTTP requests when scrubbing the seek bar.

---

## ⚡ Flashcards
1.  **What is Transcoding?**
    *   Converting a video file from one format/resolution to another to support multiple devices/speeds.
2.  **Why use Presigned URLs?**
    *   To offload the bandwidth of large file uploads from your application servers directly to the object storage (S3).
3.  **HLS vs DASH?**
    *   HLS (Apple) and DASH (Standard) are both adaptive streaming protocols that break video into chunks.
