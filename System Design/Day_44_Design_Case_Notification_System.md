# Day 44: Design Case - Notification System

## 🎯 Goal
Design a scalable notification service that can send millions of emails, SMS, and Push notifications (APNS/FCM).
**Focus**: Pluggability, Rate Limiting, and Retry Mechanisms.

---

## 🗣️ Requirements

### Functional
1.  **Send**: Support Email, SMS, Push (iOS/Android).
2.  **Bulk**: Ability to blast "Breaking News" to 10M users.
3.  **Prioritization**: OTPs > Marketing Emails.
4.  **Tracking**: Did the user open/click?

### Non-Functional
1.  **Reliability**: Messages must not be lost (At-least-once).
2.  **Scalability**: Handle spikes (New Year's Eve).
3.  **Extensibility**: Easy to add Slack/WhatsApp later.

---

## 📐 Capacity Estimation
*   **DAU**: 10 Million.
*   **Avg Notifications**: 5 per user/day = 50M notifications/day.
*   **QPS**: 50M / 86400 ≈ **600 QPS** (average).
*   **Peak**: Sports event or breaking news -> 100k QPS.
*   **Storage**: Log every notification for audit. 50M * 1KB = 50GB/day.

---

## 🏗️ System Architecture

### 1. Components
1.  **Notification Service**: Entry point API (`POST /send`). Validates input.
2.  **Message Queues (Kafka/RabbitMQ)**: Critical for buffering.
    *   Topics: `otp_sms`, `marketing_email`, `push_updates`.
3.  **Workers**: Pull from queues and call 3rd party providers.
4.  **3rd Party Providers**:
    *   Email: SendGrid / Amazon SES.
    *   SMS: Twilio / Nexmo.
    *   Push: Firebase (FCM) / Apple (APNS).

### 2. Flow
1.  **Client** calls `Notification Service`.
2.  **Service** validates and pushes event to **Kafka** (Topic based on priority/type).
    *   High Priority -> `critical_queue`.
    *   Low Priority -> `bulk_queue`.
3.  **Workers** pick up message.
4.  **Workers** call Twilio/FCM.
5.  **Workers** save status (`Sent`, `Failed`) to DB.

---

## 💻 Code Simulation: Worker with Rate Limiting

Simulating a worker that respects a rate limit (e.g., 10 SMS/sec) to avoid getting blocked by Twilio.

```python
import time
import collections

class RateLimiter:
    def __init__(self, calls, period):
        self.calls = calls
        self.period = period
        self.timestamps = collections.deque()

    def allow(self):
        now = time.time()
        # Remove timestamps older than 'period'
        while self.timestamps and self.timestamps[0] <= now - self.period:
            self.timestamps.popleft()

        if len(self.timestamps) < self.calls:
            self.timestamps.append(now)
            return True
        return False

# Worker Logic
limiter = RateLimiter(calls=5, period=1) # 5 calls per second

def process_queue(queue_items):
    for item in queue_items:
        while not limiter.allow():
            print("⏳ Rate Limit Hit. Waiting...")
            time.sleep(0.1)

        print(f"🚀 Sending: {item}")
        # Call External API here

process_queue([f"Msg {i}" for i in range(10)])
```

---

## 🧠 Deep Dive: Deduplication & Ordering
*   **Dedupe**: If a worker crashes after sending to Twilio but before Ack-ing to Kafka, the message is re-processed.
    *   *Fix*: Check `notification_id` in DB `status` table before sending.
*   **Ordering**: Not critical for most notifications.

---

## ⚡ Flashcards
1.  **Why use queues?**
    *   To decouple the ingestion (fast) from the processing (slow external API calls). Prevents system crash during spikes.
2.  **How to handle Third-Party failures?**
    *   **Retry with Exponential Backoff**. If Twilio is down, wait 2s, 4s, 8s... then move to DLQ (Dead Letter Queue).
3.  **Hard vs Soft Bounce in Email?**
    *   **Hard**: Email invalid (doesn't exist). Stop sending immediately.
    *   **Soft**: Temporary issue (inbox full). Retry later.
