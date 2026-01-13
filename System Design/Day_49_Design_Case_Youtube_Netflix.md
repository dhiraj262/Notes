# Day 49: Design Case - Youtube / Netflix

## 🎯 Goal
Design a global video streaming platform capable of handling massive upload traffic and delivering low-latency HD video.
**Focus**: Transcoding, CDN, and Adaptive Bitrate Streaming.

---

## 🗣️ Requirements

### Functional
1.  **Upload**: Users can upload videos (GBs in size).
2.  **View**: Users can stream videos instantly.
3.  **Search/Feed**: (Out of scope for this specific design, focus on media).
4.  **Quality**: Support 360p, 720p, 1080p, 4K.

### Non-Functional
1.  **Reliability**: No buffering.
2.  **Availability**: Videos always available.
3.  **Scalability**: Handle popular releases (High concurrency).

---

## 📐 Capacity Estimation
*   **Users**: 1 Billion DAU.
*   **Uploads**: 500 hours of video uploaded per minute (Youtube stats).
*   **Storage**:
    *   1 min video = 50MB (Source).
    *   Transcoded versions (SD, HD, 4K) = 100MB total.
    *   500 hrs * 60 * 100MB = **3 TB/min** -> **4 PB/day**.
*   **Bandwidth**: The biggest cost.

---

## 🧠 Core Design Decisions

### 1. Upload Protocol
*   **Problem**: Uploading a 5GB file through the API Server crashes it.
*   **Solution**: **Pre-signed URLs**.
    *   Client asks API: "I want to upload".
    *   API returns S3 URL with signature.
    *   Client uploads directly to S3 (Object Storage).

### 2. Video Processing (Transcoding)
*   **Problem**: Raw file is `.mov` (huge). Phones need `.mp4` (H.264/H.265).
*   **Solution**: Directed Acyclic Graph (DAG).
    *   Split video into 1-minute chunks.
    *   Process chunks in parallel (Audio extraction, Video encoding).
    *   Merge.
*   **Format**: **HLS (HTTP Live Streaming)** or **MPEG-DASH**.

### 3. Streaming: Adaptive Bitrate (ABS)
*   Detect user's bandwidth.
*   If slow (3G) -> Serve `chunk_1_360p.ts`.
*   If fast (WiFi) -> Serve `chunk_2_1080p.ts`.
*   Switch seamlessly without buffering.

### 4. Content Delivery Network (CDN)
*   Cache popular content at the Edge (ISP PoPs).
*   **Long Tail**: Unpopular videos stay in S3 (Origin).
*   **Netflix Open Connect**: Netflix installs its own hardware in ISP data centers.

---

## 🏗️ System Architecture

1.  **Upload Service**: Generates Pre-signed URLs. Updates Metadata DB.
2.  **Object Storage (S3)**: Stores Raw Video.
3.  **Transcoding Service (Workers)**:
    *   Listen to S3 Events.
    *   Download Raw -> FFMpeg -> Upload Transcoded chunks to S3.
4.  **CDN**: Pulls data from S3. Serves to user.
5.  **Metadata DB**: Stores video title, description, URL, user info.
6.  **Completion Service**: Updates DB when transcoding is done.

---

## 💻 Code Simulation: Transcoding Pipeline

Simulating the flow of uploading and processing a video into multiple resolutions.

```python
import time
import concurrent.futures

class VideoPlatform:
    def __init__(self):
        self.metadata_db = {} # video_id -> status
        self.cdn_links = {}   # video_id -> {res -> url}

    def upload_request(self, video_id):
        print(f"👤 User: Requesting upload for {video_id}...")
        # Simulate Pre-signed URL
        upload_url = f"https://s3.bucket.com/{video_id}"
        print(f"🌐 API: Generated Signed URL: {upload_url}")
        self.metadata_db[video_id] = "PROCESSING"

        # Trigger Transcoding (Async)
        self.trigger_transcoding(video_id)

    def trigger_transcoding(self, video_id):
        print(f"⚙️ Transcoder: Started job for {video_id}")

        # Simulate Parallel Processing of Resolutions
        resolutions = ["360p", "720p", "1080p"]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._process_res, video_id, res) for res in resolutions]
            concurrent.futures.wait(futures)

        self.metadata_db[video_id] = "READY"
        print(f"✅ Transcoder: Video {video_id} is READY.")

    def _process_res(self, video_id, res):
        print(f"   [Worker] Encoding {res}...")
        time.sleep(0.5) # Simulate CPU heavy FFMpeg
        url = f"cdn.net/{video_id}/{res}.m3u8"

        if video_id not in self.cdn_links:
            self.cdn_links[video_id] = {}
        self.cdn_links[video_id][res] = url
        print(f"   [Worker] Uploaded {res} to {url}")

    def stream(self, video_id, bandwidth_kbps):
        if self.metadata_db.get(video_id) != "READY":
            print("⚠️ Video not ready yet.")
            return

        # Adaptive Bitrate Logic
        if bandwidth_kbps < 1000:
            quality = "360p"
        elif bandwidth_kbps < 5000:
            quality = "720p"
        else:
            quality = "1080p"

        print(f"🎬 Player (BW: {bandwidth_kbps}): Playing {quality} -> {self.cdn_links[video_id][quality]}")

if __name__ == "__main__":
    youtube = VideoPlatform()
    youtube.upload_request("Cat_Video_101")

    print("\n--- Client Viewing ---")
    youtube.stream("Cat_Video_101", 500)   # Mobile Data
    youtube.stream("Cat_Video_101", 10000) # Fiber WiFi
```

**Output:**
```
👤 User: Requesting upload for Cat_Video_101...
🌐 API: Generated Signed URL: https://s3.bucket.com/Cat_Video_101
⚙️ Transcoder: Started job for Cat_Video_101
   [Worker] Encoding 360p...
   [Worker] Encoding 720p...
   [Worker] Encoding 1080p...
   [Worker] Uploaded 360p to cdn.net/Cat_Video_101/360p.m3u8
   [Worker] Uploaded 1080p to cdn.net/Cat_Video_101/1080p.m3u8
   [Worker] Uploaded 720p to cdn.net/Cat_Video_101/720p.m3u8
✅ Transcoder: Video Cat_Video_101 is READY.

--- Client Viewing ---
🎬 Player (BW: 500): Playing 360p -> cdn.net/Cat_Video_101/360p.m3u8
🎬 Player (BW: 10000): Playing 1080p -> cdn.net/Cat_Video_101/1080p.m3u8
```

---

## 🧠 Interview Nuances

### 1. Cost Optimization (CDN)
*   CDN is expensive.
*   **Strategy**: Only cache popular videos on CDN. Serve long-tail (10 views/year) directly from S3 (or a high-latency cold tier).

### 2. Deduplication
*   User A uploads "Movie.mp4". User B uploads same "Movie.mp4".
*   Check Hash (MD5) before upload. If exists, just link User B to existing file. Saves storage and compute.

### 3. DRM (Digital Rights Management)
*   Encrypt chunks.
*   Player requests decryption key from a license server.

---

## ⚡ Flashcards
1.  **What is HLS?**
    *   **HTTP Live Streaming**. Breaks video into small `.ts` chunks (10s) and uses a `.m3u8` playlist file to index them.
2.  **Why use Pre-signed URLs?**
    *   To offload binary traffic from API servers. API servers handle lightweight JSON; S3 handles heavy blobs.
3.  **Push vs Pull CDN?**
    *   **Pull**: CDN fetches from Origin on first request. (Standard).
    *   **Push**: We manually upload content to CDN. (Good for Netflix launches).
