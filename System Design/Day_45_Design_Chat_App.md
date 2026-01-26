# Day 45: Design a Chat App (WhatsApp)

## 🎯 Goal
Design a real-time messaging application like WhatsApp or Facebook Messenger.
**Focus**: Real-time delivery, Message storage (High Write Throughput), and User Status (Online/Offline).

---

## 🗣️ Requirements

### Functional
1.  **One-on-One Chat**: Send text, images, and videos.
2.  **Group Chat**: Support groups with up to 256 members.
3.  **Delivery Status**: Sent, Delivered, Read receipts.
4.  **Online Status**: Show "Last seen" or "Online".
5.  **Multi-Device Support**: Sync messages across phone and web.

### Non-Functional
1.  **Low Latency**: Real-time delivery (< 500ms).
2.  **High Availability**: 99.99% uptime.
3.  **Consistency**: Messages must be ordered (mostly).
4.  **Security**: End-to-End Encryption (E2EE).

---

## 📐 Capacity Estimation
*   **DAU**: 50 Million.
*   **Msgs/User**: 20/day.
*   **Total Messages**: 1 Billion/day.
*   **Storage**: 1B * 100 Bytes = 100 GB/day -> 36 TB/year. (Need a scalable DB).
*   **Bandwidth**: If 10% are images (1MB), immense bandwidth requirements.

---

## 🧠 Core Design Decisions

### 1. Protocol: HTTP vs WebSockets
*   **HTTP (Pull)**: Client polls server every second. Inefficient, high server load.
*   **WebSockets (Push)**: Persistent bidirectional connection. Server pushes message to client immediately.
*   **Decision**: **WebSockets** for chat. HTTP for metadata (profile update, group creation).

### 2. Database: SQL vs NoSQL
*   **Pattern**: Extremely high write throughput (1B/day). Users mostly fetch recent history.
*   **SQL (MySQL/Postgres)**: Hard to scale writes for billions of rows without complex sharding.
*   **NoSQL (Cassandra/HBase)**:
    *   **Cassandra**: Optimized for heavy writes (LSM Trees).
    *   **Data Model**: Partition by `chat_id`, sort by `timestamp`.
*   **Decision**: **Cassandra** or **HBase**.

### 3. Last Seen / Presence
*   Do not update DB on every heartbeat.
*   Use a **Heartbeat Service** with Redis.
*   Client sends heartbeat every 5s. Redis Key `user:123:status` -> `timestamp`.
*   If timestamp > 10s ago, user is Offline.

---

## 🏗️ System Architecture

1.  **Chat Service (WebSocket Server)**: Maintains open connections with active users.
    *   Map: `User_ID -> Connection_Object`.
2.  **Message Router**:
    *   User A sends msg to User B.
    *   Router checks which Chat Server holds User B's connection.
    *   Routes message there.
3.  **Cassandra**: Stores message history permanently.
4.  **Redis**: Stores "Presence" (Online/Offline status).
5.  **Push Notification Service**: If User B is offline (no WebSocket connection), send via FCM/APNS.

---

## 💻 Code Simulation: Message Router

Simulating the logic of routing a message to a connected user or falling back to DB/Push if offline.

```python
import time

class ChatSystem:
    def __init__(self):
        # Maps user_id -> socket_connection (Mock)
        self.active_sessions = {}
        # Mock DB
        self.message_store = []
        # Mock Push Service
        self.offline_queue = []

    def connect(self, user_id):
        print(f"🔌 User {user_id} connected via WebSocket.")
        self.active_sessions[user_id] = f"SocketConnection_{user_id}"

    def disconnect(self, user_id):
        if user_id in self.active_sessions:
            print(f"🔌 User {user_id} disconnected.")
            del self.active_sessions[user_id]

    def send_message(self, sender, receiver, content):
        timestamp = time.time()
        msg = {"from": sender, "to": receiver, "content": content, "ts": timestamp}

        # 1. Persist to DB (Always)
        self.message_store.append(msg)
        print(f"💾 Saved to DB: {content}")

        # 2. Attempt Real-time Delivery
        if receiver in self.active_sessions:
            conn = self.active_sessions[receiver]
            self._deliver_via_socket(conn, msg)
        else:
            # 3. Fallback to Push Notification
            self.offline_queue.append(msg)
            print(f"💤 User {receiver} offline. Pushed to Notification Service.")

    def _deliver_via_socket(self, conn, msg):
        print(f"🚀 Delivered to {msg['to']} via {conn}: {msg['content']}")

if __name__ == "__main__":
    chat = ChatSystem()

    # Users come online
    chat.connect("Alice")
    chat.connect("Bob")

    # Alice chats with Bob (Online)
    chat.send_message("Alice", "Bob", "Hello Bob!")

    # Bob goes offline
    chat.disconnect("Bob")

    # Alice sends another message
    chat.send_message("Alice", "Bob", "Are you there?")
```

**Output:**
```
🔌 User Alice connected via WebSocket.
🔌 User Bob connected via WebSocket.
💾 Saved to DB: Hello Bob!
🚀 Delivered to Bob via SocketConnection_Bob: Hello Bob!
🔌 User Bob disconnected.
💾 Saved to DB: Are you there?
💤 User Bob offline. Pushed to Notification Service.
```

---

## 🧠 Interview Nuances

### 1. Group Chat Complexity?
*   **Fan-out**: If A sends a message to a group of 500 people, the server needs to duplicate that message 500 times.
*   **Optimization**:
    *   **Small Group**: Loop and send.
    *   **Mega Group (10k users)**: Don't push. Let clients pull/poll (Hybrid approach) or use Pub/Sub topics efficiently.

### 2. Media Handling?
*   Don't send images via WebSocket.
*   Upload Image to **S3** -> Get URL -> Send URL via WebSocket.

### 3. End-to-End Encryption (E2EE)?
*   Server does not store plain text.
*   Public Key Cryptography. Alice encrypts with Bob's Public Key. Only Bob's Private Key can decrypt.
*   Server just relays the encrypted blob.

---

## ⚡ Flashcards
1.  **Why Cassandra for Chat?**
    *   Excellent write performance (LSM trees) and easy horizontal scaling/partitioning by `chat_id`.
2.  **WebSocket vs HTTP Long Polling?**
    *   WebSockets provide true full-duplex communication with lower overhead than holding an HTTP connection open.
3.  **How to handle "Read Receipts"?**
    *   When User B opens the chat, client sends an ACK. Server updates the message status in DB and pushes status update to User A.
