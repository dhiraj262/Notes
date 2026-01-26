# Day 44: Design Case - Notification System

## 🎯 Goal
Design a scalable notification service that can handle millions of Push, Email, and SMS notifications daily.
**Focus**: Pluggability, Rate Limiting, and Reliability.

---

## 🗣️ Requirements

### Functional
1.  **Send Notifications**: Support Email (SendGrid/SES), SMS (Twilio), and Push (FCM/APNS).
2.  **Bulk Send**: Send a message to 1 million users at once (e.g., "Black Friday Sale").
3.  **Prioritization**: OTPs (High) must go before Marketing (Low).
4.  **User Preferences**: Users can opt-out of SMS or Email.

### Non-Functional
1.  **High Throughput**: 10M notifications/day.
2.  **Reliability**: Never lose an OTP.
3.  **Extensibility**: Easy to add WhatsApp or Slack later.

---

## 📐 Capacity Estimation
*   **DAU**: 10 Million Users.
*   **Avg Notifications**: 5 per user/day.
*   **Total**: 50 Million requests/day.
*   **Peak**: 50M / 86400 ≈ 600 req/sec. (Easy).
*   **Spike**: Breaking news might trigger 10M messages in 5 mins -> **33k req/sec**. (Needs Kafka).

---

## 🧠 Core Design Decisions

### 1. Decoupling with Message Queues
*   **Problem**: If we call Twilio API directly for 1M users, Twilio might rate-limit us, or our server might crash waiting for responses.
*   **Solution**: `API Server` -> `Kafka` -> `Workers`.
*   **Kafka Topics**:
    *   `notif-priority-high` (OTPs)
    *   `notif-priority-low` (Marketing)

### 2. Pluggable Providers
*   Don't hardcode "Twilio". Define an `SMSProvider` interface.
*   If Twilio goes down, failover to Nexmo automatically.

### 3. User Preferences (The Filter)
*   Before sending, the worker must check `UserPreferencesDB`.
*   If User 123 has `sms_enabled = false`, drop the message.
*   *Optimization*: Cache preferences in Redis.

---

## 🏗️ System Architecture

1.  **Notification Service (API)**: Receives JSON payload. Validates params. Pushes to Kafka.
2.  **Kafka**: Stores events reliably. Partitioned by `user_id` (so one user gets messages in order).
3.  **Workers**:
    *   Read from Kafka.
    *   Check **Redis Cache** (User Preferences).
    *   Check **Rate Limiter** (Don't spam user > 5 times/hour).
    *   Call 3rd Party API (FCM/Twilio).
4.  **Retry Queue**: If Twilio fails (500 Error), push message to `retry-queue` with exponential backoff.

---

## 💻 Code Simulation: Dispatcher Logic

Simulating the core worker logic that routes messages to different providers.

```python
import queue
import time
import threading

class NotificationSystem:
    def __init__(self):
        self.queue = queue.Queue()
        self.preferences = {101: ["SMS", "PUSH"], 102: ["EMAIL"]} # Mock DB

    def ingest(self, user_id, message, channel):
        print(f"📥 API: Received {channel} for User {user_id}")
        self.queue.put({"uid": user_id, "msg": message, "chan": channel})

    def worker(self):
        while True:
            try:
                task = self.queue.get(timeout=1)
                self.process(task)
                self.queue.task_done()
            except queue.Empty:
                break # Stop if empty for 1s

    def process(self, task):
        uid, chan = task['uid'], task['chan']

        # 1. Check Preferences
        allowed_channels = self.preferences.get(uid, [])
        if chan not in allowed_channels:
            print(f"   ⛔ Blocked: User {uid} opted out of {chan}")
            return

        # 2. Mock Sending
        if chan == "SMS":
            print(f"   📱 [Twilio] Sent to {uid}: {task['msg']}")
        elif chan == "EMAIL":
            print(f"   📧 [SendGrid] Sent to {uid}: {task['msg']}")
        elif chan == "PUSH":
            print(f"   🔔 [FCM] Sent to {uid}: {task['msg']}")

if __name__ == "__main__":
    system = NotificationSystem()

    # Start Worker
    threading.Thread(target=system.worker).start()

    # Send Requests
    system.ingest(101, "Your OTP is 9988", "SMS")  # Allowed
    system.ingest(101, "Buy Now!", "EMAIL")        # Blocked (Opt-out)
    system.ingest(102, "Welcome!", "EMAIL")        # Allowed
```

**Output:**
```
📥 API: Received SMS for User 101
📥 API: Received EMAIL for User 101
📥 API: Received EMAIL for User 102
   📱 [Twilio] Sent to 101: Your OTP is 9988
   ⛔ Blocked: User 101 opted out of EMAIL
   📧 [SendGrid] Sent to 102: Welcome!
```

---

## 🧠 Interview Nuances

### 1. How to prevent spamming users?
*   **Rate Limiting**: Implement a check in the worker using Redis.
    *   Key: `rate_limit:user_123:sms` -> Value: `count`. Expiry: `1 hour`.
    *   If count > 5, drop message.

### 2. Deduplication?
*   If the Producer retries and sends the same "Welcome Email" twice.
*   Use a `msg_id` to deduplicate in Redis before sending.

### 3. Analytics (Tracking Open Rates)?
*   For Email: Embed a 1x1 transparent pixel image `<img src="tracking.com/open?id=123">`.
*   For Links: Wrap links with a URL Shortener to track clicks.

---

## ⚡ Flashcards
1.  **What is Exponential Backoff?**
    *   Waiting longer between retries (1s, 2s, 4s, 8s) to avoid hammering a failing service.
2.  **Why prioritize OTPs over Marketing?**
    *   OTP blocks the user (Login). Marketing is optional. Use separate queues.
3.  **Push vs Pull for Notification Service?**
    *   The Notification Service acts as a **Push** system to the end user, but internally it **Pulls** from the Kafka queue.
