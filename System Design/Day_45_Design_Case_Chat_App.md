# Day 45: Design a Chat App (WhatsApp/Discord)

## 🎯 Goal
Design a real-time messaging system supporting 1-on-1 and Group chats.
**Focus**: Low Latency, Message Ordering, and "Sent/Delivered/Read" Status.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Real-time text exchange.
2.  **Group Chat**: Up to 256 members.
3.  **Online Status**: Show if a user is Online/Offline.
4.  **Message Status**: Sent (1 tick), Delivered (2 ticks), Read (Blue ticks).
5.  **Persistent History**: Messages must be stored permanently.

### Non-Functional
1.  **Low Latency**: < 100ms for message delivery.
2.  **High Availability**: 99.999% uptime.
3.  **Scale**: 2 Billion Users (WhatsApp scale). 100B messages/day.

---

## 📐 Capacity Estimation
*   **DAU**: 1 Billion.
*   **Msgs/User**: 50/day.
*   **Total Msgs**: 50 Billion/day.
*   **Storage**: 50B * 100 Bytes = 5 TB/day -> **1.8 PB/year**.
    *   *Conclusion*: We need a highly scalable NoSQL DB (Cassandra/HBase) for history.
*   **Bandwidth**: Media files (Images/Videos) will dominate bandwidth, handled by CDN/Object Storage (S3).

---

## 🧠 Core Design Decisions

### 1. Communication Protocol: WebSocket vs HTTP
*   **HTTP**: Request/Response. Good for fetching history. Bad for real-time.
*   **Polling**: High latency, server load.
*   **WebSocket**: Bi-directional, persistent connection.
    *   *Decision*: **WebSockets** for sending/receiving messages. HTTP for profile updates/media upload.

### 2. Database Choice
*   **RDBMS (MySQL/Postgres)**: Good for user profiles/friends. Bad for 50B rows/day.
*   **NoSQL (Cassandra)**: Excellent for heavy write throughput.
    *   *Schema*: Partition Key = `chat_id`. Cluster Key = `message_id` (TimeUUID). This sorts messages by time automatically.

### 3. Handling Offline Users
*   If User B is offline, User A's message goes to the **Message Store** DB.
*   When User B comes online, they pull "unread messages" from the DB.

---

## 🏗️ System Architecture

1.  **Chat Service (WebSocket Server)**: Maintains active connections. Stateful.
    *   Uses **Redis** to store "User A is connected to Server Node 3".
2.  **Message Service (API)**: Handles message persistence.
3.  **Group Service**: Manages group metadata (members, admins).
4.  **Presence Service**: Heartbeat mechanism to track Online/Last Seen.
5.  **Push Notification Service**: Triggers FCM/APNS if user is disconnected.

### The Flow (User A -> User B)
1.  User A sends msg via WebSocket to Chat Server.
2.  Server saves msg to **Cassandra**.
3.  Server looks up User B's connection in **Redis**.
4.  **If Online**: Route msg to the specific Chat Server node holding User B's connection -> Push to User B.
5.  **If Offline**: Trigger Push Notification.

---

## 💻 Code Simulation: WebSocket Routing Logic

Simulating the core "Online vs Offline" routing logic.

```python
import threading
import time
import queue

class ChatServer:
    def __init__(self):
        # Maps user_id -> queue.Queue (simulating a WebSocket connection)
        self.connections = {}
        self.lock = threading.Lock()

        # Message Store: {chat_id: [messages]}
        self.message_store = {}

    def connect(self, user_id):
        with self.lock:
            self.connections[user_id] = queue.Queue()
            print(f"✅ User {user_id} connected.")
        return self.connections[user_id]

    def send_message(self, sender_id, receiver_id, content):
        timestamp = time.time()
        msg_obj = {"from": sender_id, "to": receiver_id, "content": content, "ts": timestamp}

        # 1. Store Message
        chat_id = tuple(sorted((sender_id, receiver_id)))
        if chat_id not in self.message_store:
            self.message_store[chat_id] = []
        self.message_store[chat_id].append(msg_obj)
        print(f"💾 Stored: {content} (Chat: {chat_id})")

        # 2. Push to Receiver (if connected)
        with self.lock:
            if receiver_id in self.connections:
                self.connections[receiver_id].put(msg_obj)
                print(f"🚀 Pushed to {receiver_id}: {content}")
            else:
                print(f"💤 {receiver_id} is offline. Message saved for later.")

def user_client(user_id, server):
    conn = server.connect(user_id)
    while True:
        try:
            # Simulate waiting for messages via WebSocket
            msg = conn.get(timeout=2)
            print(f"👤 User {user_id} received: '{msg['content']}' from {msg['from']}")
        except queue.Empty:
            break # Exit after silence

if __name__ == "__main__":
    server = ChatServer()

    # Start Alice listening
    t1 = threading.Thread(target=user_client, args=("Alice", server))
    t1.start()

    # Start Bob listening
    t2 = threading.Thread(target=user_client, args=("Bob", server))
    t2.start()

    time.sleep(1)

    # Alice sends to Bob
    server.send_message("Alice", "Bob", "Hello Bob!")
    time.sleep(0.5)

    # Bob sends to Alice
    server.send_message("Bob", "Alice", "Hey Alice, how are you?")

    # Alice sends to offline Dave
    server.send_message("Alice", "Dave", "Are you there?")

    t1.join()
    t2.join()
```

---

## 🧠 Interview Nuances

### 1. How to handle Group Chats?
*   **Small Group (< 100)**: Iterate members and push to all.
*   **Mega Group (1M members)**: Don't push. Let members **Pull** or use Pub/Sub with Kafka.

### 2. "Last Seen" Scalability?
*   Do not write to DB on every heartbeat.
*   Update Redis every 5s.
*   Flush Redis to DB only on disconnect or every 5 mins.

### 3. End-to-End Encryption (E2EE)?
*   The server only stores encrypted blobs. It cannot read messages.
*   Keys are exchanged between devices (Signal Protocol).

---

## ⚡ Flashcards
1.  **WebSocket vs HTTP Long Polling?**
    *   WebSocket is full-duplex (server can push). Long Polling is half-duplex (client asks, server holds).
2.  **Why Cassandra for Chat?**
    *   Write-heavy workload. Time-series data (Chat History). Linear scalability.
3.  **What is a "Fan-out" in Group Chat?**
    *   The process of delivering one message to N group members. Can be "Write Fan-out" (store N copies) or "Read Fan-out" (store 1, N people read it).
