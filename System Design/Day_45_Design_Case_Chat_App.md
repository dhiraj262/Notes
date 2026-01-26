# Day 45: Design Case - Chat App (WhatsApp)

## 🎯 Goal
Design a real-time chat application similar to WhatsApp or Facebook Messenger.
**Focus**: Low Latency, High Throughput, Message Delivery Guarantee.

---

## 🗣️ Requirements

### Functional
1.  **One-on-One Chat**: Real-time messaging between two users.
2.  **Group Chat**: Messaging within a group (max 256 members).
3.  **Online Presence**: Show if a user is "Online" or "Last Seen".
4.  **Media Sharing**: Images/Videos (optional, but affects storage).
5.  **Read Receipts**: Sent, Delivered, Read ticks.

### Non-Functional
1.  **Low Latency**: Real-time experience (< 100ms).
2.  **Consistency**: Messages must appear in order.
3.  **Availability**: High availability, but CAP theorem implies consistency is critical for history.
4.  **Scale**: 1 Billion users, 100 Billion messages/day.

---

## 📐 Capacity Estimation
*   **DAU**: 500 Million Users.
*   **Msgs/User**: 40 messages/day.
*   **Total Messages**: 20 Billion/day.
*   **QPS**: 20B / 86400 ≈ **230k msg/sec**.
*   **Peak**: 230k * 3 ≈ **700k msg/sec**.
*   **Storage**:
    *   Avg msg size = 100 bytes.
    *   Daily storage = 20B * 100B = 2TB/day.
    *   5 Years = 2TB * 365 * 5 ≈ **3.6 PB**.

---

## 🧠 Core Design Decisions

### 1. Communication Protocol: WebSocket
*   **Polling (HTTP)**: Client asks "Any new msg?" every 2s. High server load, latency.
*   **Long Polling**: Client waits until server has data. Better, but still header overhead.
*   **WebSocket**: Full-duplex persistent connection. Best for real-time chat.
*   **Decision**: Use **WebSockets** for active sessions. Use **Push Notifications** (FCM/APNS) for offline users.

### 2. Database Choice: Cassandra/HBase (NoSQL)
*   **SQL (MySQL/Postgres)**: Good for small scale. Scaling writes to 700k/sec requires massive sharding.
*   **NoSQL (Cassandra)**: Excellent write throughput. Efficient range queries (fetch last 50 msgs for ChatID).
*   **Data Model**:
    *   `Partition Key`: `ChatID` (stores all msgs for a conversation together).
    *   `Clustering Key`: `Timestamp` (orders messages by time).

### 3. Message Synchronization (Sequence IDs)
*   Distributed clocks are unreliable.
*   Use a monotonically increasing Sequence ID per chat.
*   The client keeps track of `last_seq_id`. When reconnecting, asks server "Give me msgs > last_seq_id".

---

## 🏗️ System Architecture

1.  **Chat Service (WebSocket Server)**: Maintains persistent connections with online users. Statefull (needs Sticky Sessions or Redis Pub/Sub to route messages).
2.  **Presence Service**: Tracks "Online/Offline". Uses Redis Heartbeat (TTL 10s).
3.  **Message Store**: Cassandra/HBase. Stores chat history.
4.  **Push Notification Service**: If user is not connected to WebSocket, send Push.
5.  **Asset Service**: S3/CDN for images/videos.

**Flow (User A sends to User B):**
1.  User A sends msg to `Chat Service`.
2.  Server assigns `MessageID` and Timestamp.
3.  Server saves to `Message Store` (Cassandra).
4.  Server checks `Presence Service` for User B.
    *   If **Online**: Find which Chat Server holds B's connection. Forward msg via Redis Pub/Sub. Push to B via WebSocket.
    *   If **Offline**: Send to `Push Notification Service`.

---

## 💻 Code Simulation: Simple WebSocket Chat

Simulating a chat server that handles connections and broadcasts messages.

```python
import threading
import time
import queue

class ChatServer:
    def __init__(self):
        self.clients = {} # user_id -> queue
        self.lock = threading.Lock()

    def connect(self, user_id):
        with self.lock:
            self.clients[user_id] = queue.Queue()
        print(f"✅ User {user_id} Connected")

    def disconnect(self, user_id):
        with self.lock:
            if user_id in self.clients:
                del self.clients[user_id]
        print(f"❌ User {user_id} Disconnected")

    def send_message(self, sender, receiver, content):
        timestamp = time.strftime('%H:%M:%S')
        msg_obj = {"from": sender, "content": content, "time": timestamp}

        # Save to DB (Mock)
        print(f"💾 Saved to DB: {msg_obj}")

        with self.lock:
            if receiver in self.clients:
                self.clients[receiver].put(msg_obj)
                print(f"🚀 Delivered to {receiver} via WebSocket")
            else:
                print(f"🔔 User {receiver} Offline. Sent Push Notification.")

    def listen(self, user_id):
        """ Simulates the client listening loop """
        q = self.clients.get(user_id)
        if not q: return
        while True:
            try:
                msg = q.get(timeout=1)
                print(f"📩 User {user_id} received: {msg['content']} from {msg['from']}")
            except queue.Empty:
                break # Just for simulation, stop if empty

if __name__ == "__main__":
    server = ChatServer()

    # Users connect
    server.connect("Alice")
    server.connect("Bob")

    # Chatting
    server.send_message("Alice", "Bob", "Hello Bob!")

    # Receive
    threading.Thread(target=server.listen, args=("Bob",)).start()
    time.sleep(2)

    # Offline scenario
    server.disconnect("Bob")
    server.send_message("Alice", "Bob", "Are you there?")
```

**Output:**
```
✅ User Alice Connected
✅ User Bob Connected
💾 Saved to DB: {'from': 'Alice', 'content': 'Hello Bob!', 'time': '...'}
🚀 Delivered to Bob via WebSocket
📩 User Bob received: Hello Bob! from Alice
❌ User Bob Disconnected
💾 Saved to DB: {'from': 'Alice', 'content': 'Are you there?', 'time': '...'}
🔔 User Bob Offline. Sent Push Notification.
```

---

## 🧠 Interview Nuances

### 1. How to handle Group Chats?
*   **Write Amplification**: Storing a copy for every user is expensive.
*   **Read Amplification**: Storing once (referenced by GroupID) means every user queries the same row.
*   **Solution**: Store message once with `GroupID`.
    *   For delivery: Server looks up `GroupMembers` (cached in Redis), loops through them, and pushes via WebSocket.

### 2. "Last Seen" feature scaling?
*   Don't write to DB on every heartbeat.
*   Update Redis every 5 seconds.
*   Only persist to DB (Cassandra) when user disconnects or every 5 mins.

### 3. End-to-End Encryption (E2EE)?
*   Server stores encrypted blob. Server cannot read the message.
*   Keys are exchanged between clients (Signal Protocol).

---

## ⚡ Flashcards
1.  **WebSocket vs HTTP for Chat?**
    *   WebSocket is persistent and bi-directional. HTTP is req-resp (high overhead for real-time).
2.  **Why NoSQL (Cassandra) for Chat History?**
    *   Chat logs are write-heavy and append-only. Cassandra handles high write throughput and partitions well by ChatID.
3.  **What is a "Sticky Session"?**
    *   Ensuring a client's WebSocket connection stays on the same server for the duration of the session.
