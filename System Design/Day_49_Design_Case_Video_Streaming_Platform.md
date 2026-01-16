# Day 49: Design Youtube/Netflix (Video Streaming)

## 🎯 Goal
Design a Video On Demand (VOD) platform that supports uploading, processing (transcoding), and low-latency streaming to millions of concurrent users globally.

## 📋 Requirements

### Functional
1.  **Upload**: Users upload videos.
2.  **Transcoding**: Convert raw video to multiple formats/resolutions (720p, 1080p, Mobile).
3.  **Streaming**: Smooth playback with Adaptive Bitrate Streaming (ABS).
4.  **Content Delivery**: Low latency via CDN.

### Non-Functional
1.  **Scalability**: Support viral videos (Million views/hour).
2.  **Availability**: Playback must never fail.
3.  **Performance**: Minimal buffering (Start time < 200ms).
4.  **Storage**: Massive cold storage requirements.

## 🔢 Capacity Estimation

*   **DAU**: 100 Million.
*   **Watch Time**: 5 videos/day.
*   **Traffic**: 500 Million views/day.
*   **Storage**:
    *   100k videos uploaded/day.
    *   Avg size 500MB.
    *   Total Daily Storage = 50 TB/day (Originals) + Transcoded versions.

## 🏗️ Architecture Design

### 1. Upload Flow (Pre-signed URLs)
*   **Problem**: Uploading huge files to the API server blocks threads.
*   **Solution**:
    1.  Client requests upload URL.
    2.  Server returns a **Pre-signed URL** (S3).
    3.  Client uploads directly to Object Storage (S3).

### 2. Video Processing (The DAG)
Once uploaded, the video must be processed.
*   **Split**: Split video into chunks (GOP - Group of Pictures).
*   **Transcode**: Convert each chunk to different resolutions (360p, 720p, 4k) and codecs (H.264, VP9).
*   **Parallelism**: This is a compute-heavy task. Use a directed acyclic graph (DAG) of tasks (e.g., AWS Step Functions or Airflow).
*   **Output**: Generate **HLS (.m3u8)** or **DASH (.mpd)** playlists.

### 3. Content Delivery (CDN)
*   **Strategy**: Push popular content to Edge Servers (CDN).
*   **Tiered Cache**:
    *   Tier 1: ISP Edge (Super popular).
    *   Tier 2: Regional IXP (Popular).
    *   Origin: S3 (Long tail content).

### 4. Adaptive Bitrate Streaming (ABS)
*   **Problem**: Network fluctuates.
*   **Solution**: The player (Client) detects bandwidth and requests the appropriate chunk quality.
    *   If net is slow -> Request `chunk_1_360p.ts`.
    *   If net is fast -> Request `chunk_2_1080p.ts`.

## 🐍 Code Simulation
Python simulation of **Adaptive Bitrate Selection** logic.

```python
class AdaptiveStreamer:
    def __init__(self, available_bitrates):
        # bitrates in kbps: e.g., {360: 500, 720: 1500, 1080: 3000}
        self.available_bitrates = available_bitrates
        self.last_bandwidth_sample = 0 # kbps

    def measure_bandwidth(self, chunk_size_kb, download_time_sec):
        # Simple bandwidth estimation
        if download_time_sec == 0: return
        self.last_bandwidth_sample = chunk_size_kb / download_time_sec
        print(f"[Network] Speed: {self.last_bandwidth_sample:.2f} kbps")

    def select_quality(self):
        # Logic: Pick highest quality < 80% of bandwidth (safety margin)
        safe_bandwidth = self.last_bandwidth_sample * 0.8

        selected_res = 0
        selected_bitrate = 0

        # Sort available options by bitrate
        sorted_opts = sorted(self.available_bitrates.items(), key=lambda x: x[1])

        for res, bitrate in sorted_opts:
            if bitrate <= safe_bandwidth:
                selected_res = res
                selected_bitrate = bitrate
            else:
                break

        # Fallback: If network is too slow, pick lowest quality
        if selected_res == 0:
            selected_res = sorted_opts[0][0]
            selected_bitrate = sorted_opts[0][1]

        print(f"[Player] Switching to {selected_res}p ({selected_bitrate} kbps)")
        return selected_res

# --- Driver Code ---
if __name__ == "__main__":
    streamer = AdaptiveStreamer({360: 400, 720: 1500, 1080: 4500, 1440: 8000})

    # Scenario 1: Fast Internet
    print("--- Scenario 1: Fast Internet ---")
    streamer.measure_bandwidth(5000, 0.5) # 10000 kbps
    streamer.select_quality() # Should pick 1440p

    # Scenario 2: Slow Internet
    print("\n--- Scenario 2: Slow Internet ---")
    streamer.measure_bandwidth(500, 1.0) # 500 kbps
    streamer.select_quality() # Should pick 360p
```

## 🧠 Interview Nuances

### "The Trap": Storing one big file
*   **Problem**: If you store a 1GB MP4, the user has to download the whole header to start, and seeking is slow.
*   **Solution**: **Chunking**. Break video into 4-second segments (`.ts` files). This allows efficient CDN caching and bitrate switching.

### "The Kill Shot": DRM & Security
*   **Challenge**: "How do you prevent users from downloading the video?"
*   **Solution**: **Widevine / FairPlay DRM**.
    *   Encrypt the video chunks.
    *   Player requests a License Key from a License Server.
    *   License Server verifies user token and subscription before issuing the decryption key.

### "Production Realities"
*   **Open Connect (Netflix)**: Netflix builds its own CDN hardware and places it physically inside ISP data centers to save bandwidth costs.
*   **Long Tail**: 80% of videos are rarely watched. Keep them on S3 (Standard or Infrequent Access). Only cache the top 20%.

## ⚡ Flashcards
*   **Upload Method?** -> Pre-signed URLs (S3).
*   **Streaming Protocol?** -> HLS (Apple) or DASH.
*   **Client Logic?** -> Adaptive Bitrate Streaming (ABS).
*   **Processing?** -> DAG (Split -> Transcode -> Merge).
