# Day 45: Design Case - Chat App (WhatsApp/Messenger)

## 🎯 Goal
Design a large-scale chat application supporting 1-on-1 and Group chats with real-time delivery and persistent storage.
**Focus**: Low Latency, Consistency (Message Ordering), and Availability.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Real-time messaging between two users.
2.  **Group Chat**: Messages delivered to all group members (up to 256 members).
3.  **Delivery Status**: Sent, Delivered, Read receipts.
4.  **Online Status**: Show if a user is online/offline/last seen.
5.  **Media**: Support for images/videos (handled via HTTP/Object Storage).

### Non-Functional
1.  **Low Latency**: Real-time experience (< 100ms).
2.  **High Availability**: Always accept writes (messages).
3.  **Consistency**: Messages must be ordered correctly.
4.  **Scale**: 1 Billion DAU.

---

## 📐 Capacity Estimation
*   **DAU**: 1 Billion.
*   **Messages**: 40 messages/user/day -> 40 Billion messages/day.
*   **Storage**: 40B * 100 bytes ≈ 4TB/day. 5 Years ≈ 7PB.
*   **Bandwidth**: Text is low, media is high.
*   **QPS**: 40B / 86400 ≈ 460k msg/sec average. Peak ≈ 1M msg/sec.

---

## 🧠 Core Design Decisions

### 1. Protocol: WebSocket vs HTTP
*   **Problem**: HTTP is request-response. Not ideal for server-pushing messages to receiver.
*   **Solution**: **WebSockets**. Long-lived bi-directional connection.
    *   Client keeps a connection open to a `Chat Server`.
    *   Server pushes messages instantly.

### 2. Database: SQL vs NoSQL
*   **Access Pattern**: Read recent messages often. Write throughput is high.
*   **SQL (MySQL/Postgres)**: Good for relations, but scaling writes to 1M/sec is hard (needs sharding).
*   **NoSQL (Cassandra/HBase)**: Excellent for heavy writes.
    *   **Cassandra/ScyllaDB**: Partition Key = `chat_id` (or `user_id` for 1-on-1), Sort Key = `message_id` (time based).
    *   Discord uses Cassandra/ScyllaDB. Facebook Messenger uses HBase.

### 3. Message ID Generator
*   Must be sortable by time.
*   Use **Snowflake ID** or KSUID.
*   Allows enforcing order even in distributed systems.

---

## 🏗️ System Architecture

1.  **Chat Service (WebSocket)**: Holds active connections.
    *   User A connects to Server 1.
    *   User B connects to Server 2.
    *   If A sends to B, Server 1 forwards to Server 2 (via Redis Pub/Sub or internal routing).
2.  **Service Discovery**: Zookeeper/Etcd to know which user is connected to which server.
3.  **Message Store**: Cassandra/HBase for history.
4.  **Offline Inbox**: If User B is offline, store in `Unread_Queue` or just database with `delivered=False`.
5.  **Group Service**: Manages group members. For Group Chat, sender sends 1 msg, server expands to N members.

---

## 💻 Code Simulation: Chat Server Logic

A simplified simulation of how a server handles online vs offline routing.

```python
import time
from collections import defaultdict

class ChatSystem:
    def __init__(self):
        self.users = {}  # user_id -> User Session
        self.messages = defaultdict(list)  # user_id -> [messages] (Offline Store)
        self.online_status = {} # user_id -> bool

    def connect(self, user_id):
        self.online_status[user_id] = True
        print(f"🟢 User {user_id} is Online")
        # Deliver pending messages
        if self.messages[user_id]:
            print(f"   📩 Delivering pending messages to {user_id}...")
            for msg in self.messages[user_id]:
                print(f"      [From {msg['from']}]: {msg['text']}")
            self.messages[user_id] = [] # Clear offline inbox

    def disconnect(self, user_id):
        self.online_status[user_id] = False
        print(f"🔴 User {user_id} is Offline")

    def send_message(self, sender_id, receiver_id, text):
        msg = {'from': sender_id, 'text': text, 'timestamp': time.time()}

        # Check if receiver is online
        if self.online_status.get(receiver_id):
            # In real system: Push via WebSocket
            print(f"🚀 [Direct] {sender_id} -> {receiver_id}: {text}")
        else:
            # Store in DB/Offline Queue
            print(f"💾 [Stored] {sender_id} -> {receiver_id}: {text}")
            self.messages[receiver_id].append(msg)

if __name__ == "__main__":
    chat = ChatSystem()

    # 1. Alice connects
    chat.connect("Alice")

    # 2. Alice sends message to Bob (who is Offline)
    chat.send_message("Alice", "Bob", "Hello Bob, are you there?")

    # 3. Bob connects later
    chat.connect("Bob")

    # 4. Bob replies immediately
    chat.send_message("Bob", "Alice", "Hi Alice! I'm here now.")

    chat.disconnect("Alice")
```

**Output:**
```
🟢 User Alice is Online
💾 [Stored] Alice -> Bob: Hello Bob, are you there?
🟢 User Bob is Online
   📩 Delivering pending messages to Bob...
      [From Alice]: Hello Bob, are you there?
🚀 [Direct] Bob -> Alice: Hi Alice! I'm here now.
🔴 User Alice is Offline
```

---

## 🧠 Interview Nuances

### 1. How to handle "Last Seen"?
*   **Heartbeats**: Client sends heartbeat every 5s.
*   **Redis**: Store `last_active_time` in Redis.
*   When user A opens chat with B, query Redis for B's time.

### 2. Group Chat Scaling?
*   **Small Groups (WhatsApp)**: Server replicates message to each member's queue. (Client-side fanout or Server-side small fanout).
*   **Mega Groups (Discord/Telegram)**: Only push to online members. Fetch history for others on demand.

### 3. Encryption (E2EE)?
*   **Signal Protocol**: Messages encrypted on device. Server can't read them.
*   Keys exchanged during initial handshake (Pre-Keys).

---

## ⚡ Flashcards
1.  **Why WebSocket over HTTP for Chat?**
    *   WebSocket allows full-duplex communication (Server can push to Client), reducing latency and overhead compared to Polling.
2.  **What database is best for Chat History?**
    *   Wide-column NoSQL (Cassandra/HBase) due to high write throughput and query-by-time patterns.
3.  **How to handle multiple devices?**
    *   Synchronize state via a common inbox in the database. When one device reads, update status for all.
