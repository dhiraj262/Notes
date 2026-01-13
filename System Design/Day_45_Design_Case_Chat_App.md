# Day 45: Design Case - Chat App (WhatsApp/Telegram)

## 🎯 Goal
Design a real-time chat application similar to WhatsApp or Telegram that supports 1-on-1 and Group messaging.
**Focus**: Low Latency, High Availability, and Delivery Semantics.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Real-time message delivery.
2.  **Group Chat**: Support groups with up to 256 members.
3.  **Status Indicators**: Sent, Delivered, Read.
4.  **Online/Offline Status**: Show if a user is online.
5.  **Media**: Support sending images/videos (Briefly).

### Non-Functional
1.  **Low Latency**: Real-time experience (< 100ms).
2.  **Consistency**: Messages must be ordered (FIFO).
3.  **Availability**: Always writeable (CAP Theorem: AP or CP?).
4.  **Security**: End-to-End Encryption (Optional for interview scope).

---

## 📐 Capacity Estimation
*   **DAU**: 2 Billion Users (WhatsApp scale).
*   **Messages**: 50 per user/day -> **100 Billion msgs/day**.
*   **QPS**: 100B / 86400 ≈ **1.2 Million msgs/sec**.
*   **Storage**: 100B * 50 bytes (avg) = **5 TB/day** (Text only).
*   **Bandwidth**: High.

---

## 🧠 Core Design Decisions

### 1. Protocol: HTTP vs WebSockets
*   **HTTP (Pull)**: Client polls every second. Too much overhead/latency.
*   **WebSockets (Push)**: Persistent bi-directional connection. Server pushes message to client instantly.
*   **Decision**: **WebSockets** for real-time delivery.

### 2. Database: SQL vs NoSQL
*   **Access Pattern**: Write-heavy, Read-sequential (History).
*   **SQL**: Hard to scale to 100B writes/day.
*   **NoSQL (LSM Tree)**: **Cassandra** or **HBase**. Optimized for heavy writes and range scans (fetch last 50 msgs).
*   **Decision**: **Cassandra/HBase**. Key: `chat_id` + `timestamp`.

### 3. Message Delivery Flow
*   User A -> Load Balancer -> Chat Server (WebSocket) -> User B.
*   **If User B is Offline?** Store in DB. When B connects, push pending messages.

---

## 🏗️ System Architecture

1.  **Chat Service (Stateful)**: Maintains WebSocket connections. Map: `user_id` -> `socket_connection`.
2.  **Presence Service**: Redis-backed. `SET user:123:status "ONLINE" EX 30`. Heartbeats keep it alive.
3.  **Message Queue**: Kafka. To decouple ingestion from processing (Push notifications, Analytics).
4.  **Database**: Cassandra cluster for chat history.
5.  **Push Notification**: If WebSocket is broken/offline, fall back to FCM/APNS.

### The "Store-and-Forward" Model
1.  **Bob sends to Alice**.
2.  Server saves to **Cassandra** (Msg ID: 101, Status: SENT).
3.  Server checks Redis: Is Alice Online?
    *   **Yes**: Send via WebSocket. Update Status -> DELIVERED.
    *   **No**: Trigger Push Notification.

---

## 💻 Code Simulation: WebSocket Server Logic

Simulating the core routing logic for a WebSocket-based chat server.

```python
import time
import collections
import threading

class ChatServer:
    def __init__(self):
        # Maps user_id -> mock_socket_connection
        self.connected_sockets = {}
        # Emulating a Database for offline messages
        self.offline_store = collections.defaultdict(list)

    def connect(self, user_id):
        self.connected_sockets[user_id] = f"WS_CONN_{user_id}"
        print(f"✅ User {user_id} CONNECTED.")

        # Check for offline messages
        if self.offline_store[user_id]:
            print(f"   📬 Delivering {len(self.offline_store[user_id])} pending messages to {user_id}...")
            for msg in self.offline_store[user_id]:
                print(f"      -> {msg}")
            self.offline_store[user_id] = [] # Clear DB

    def disconnect(self, user_id):
        if user_id in self.connected_sockets:
            del self.connected_sockets[user_id]
            print(f"❌ User {user_id} DISCONNECTED.")

    def send_message(self, sender, receiver, content):
        timestamp = time.time()
        print(f"📤 [Msg] {sender} -> {receiver}: '{content}'")

        if receiver in self.connected_sockets:
            # Real-time delivery
            socket = self.connected_sockets[receiver]
            print(f"   🚀 Pushed to {socket} (Online)")
            return "DELIVERED"
        else:
            # Store for later
            self.offline_store[receiver].append({"from": sender, "text": content, "ts": timestamp})
            print(f"   💾 stored in DB (User Offline)")
            return "SENT"

if __name__ == "__main__":
    server = ChatServer()

    # Scenario
    server.connect("Alice")
    server.connect("Bob")

    server.send_message("Alice", "Bob", "Hey Bob!")

    server.disconnect("Bob")
    server.send_message("Alice", "Bob", "Are you there?")

    server.connect("Bob") # Reconnects, gets message
```

**Output:**
```
✅ User Alice CONNECTED.
✅ User Bob CONNECTED.
📤 [Msg] Alice -> Bob: 'Hey Bob!'
   🚀 Pushed to WS_CONN_Bob (Online)
❌ User Bob DISCONNECTED.
📤 [Msg] Alice -> Bob: 'Are you there?'
   💾 stored in DB (User Offline)
✅ User Bob CONNECTED.
   📬 Delivering 1 pending messages to Bob...
      -> {'from': 'Alice', 'text': 'Are you there?', 'ts': ...}
```

---

## 🧠 Interview Nuances

### 1. Group Chat: Read Receipts
*   **Trap**: Don't update the message row for every read receipt (Write amplification).
*   **Fix**: Store `last_read_message_id` for each user-group pair.
*   `GroupMember(group_id, user_id, last_read_id)`.

### 2. Media Files
*   Don't send binary data over WebSocket/MessageQueue.
*   **Flow**:
    1.  Client uploads Image to **S3/Blob Storage**.
    2.  Get URL (`s3.aws.com/img.jpg`).
    3.  Send Chat Message with text: `None` and attachment_url: `...`.

### 3. Sequence Numbers
*   How to keep messages in order?
*   Use a **Sequence Generator** (Snowflake ID) that is sortable by time.
*   Cassandra Clustering Key orders by ID automatically.

---

## ⚡ Flashcards
1.  **Why WebSocket over HTTP?**
    *   Lower overhead (header compression), Full-duplex (Server can push).
2.  **Long Polling vs WebSockets?**
    *   Long Polling holds a request open. Good for low frequency updates. WebSockets better for chat/gaming.
3.  **Fan-out on Read vs Write (Group Chat)?**
    *   **Write**: Sender creates 1 message, server copies to 100 inboxes. (Faster read, Slower write).
    *   **Read**: Sender writes 1 message to Group ID. Users pull from Group ID. (Better for mega-groups).
