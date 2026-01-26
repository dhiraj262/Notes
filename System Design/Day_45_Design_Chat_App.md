# Day 45: Design a Chat App (WhatsApp/Telegram)

## 🎯 Goal
Design a real-time messaging system like WhatsApp, Facebook Messenger, or WeChat.
**Focus**: Real-time delivery (WebSockets), Scale (Billions of msgs), and Status (Online/Offline).

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Low latency delivery.
2.  **Group Chat**: Support groups of up to 256 members.
3.  **Online Status**: Show if a user is Online/Offline/Typing.
4.  **Media Support**: Images, Videos (Not focused on deep storage details here, but the mechanism).
5.  **Multi-Device**: Sync across Phone and Web.

### Non-Functional
1.  **Low Latency**: Messages must feel instant (< 100ms).
2.  **Consistency**: Messages must be ordered correctly.
3.  **Availability**: High availability for sending messages (CAP -> AP usually, but Consistency matters for chat history).
4.  **Encryption**: End-to-End (E2EE) - though we focus on system architecture first.

---

## 📐 Capacity Estimation
*   **DAU**: 500 Million Users.
*   **Msgs/User**: 40 daily.
*   **Total Messages**: 20 Billion / day.
*   **Storage**: Assuming 100 bytes/msg -> 2TB / day. (Need heavy archival strategy).
*   **Peak Traffic**: 20B / 86400 ≈ 230k msg/sec.
*   **WebSockets**: 500M concurrent connections (Need massive server fleet).

---

## 🧠 Core Design Decisions

### 1. HTTP vs WebSockets
*   **HTTP (Polling)**: "Are there new messages?" -> Inefficient, high latency, server load.
*   **Long Polling**: Better, but still overhead.
*   **WebSockets**: Bi-directional, persistent connection. Best for Chat.
    *   *Decision*: Use **WebSockets** for message delivery.

### 2. Database Choice (Read/Write Heavy)
*   **SQL (MySQL/Postgres)**: Good for relations, but scaling writes for 20B/day is hard. Indexing becomes slow.
*   **NoSQL (Cassandra/HBase)**: Excellent for heavy writes.
    *   *Decision*: **Cassandra/HBase** (Wide-Column Store) or **DynamoDB**.
    *   *Schema*: Partition Key = `chat_id` (or `user_id` for inbox), Sort Key = `timestamp`.

### 3. Message Synchronization
*   How to handle offline users?
*   Use a temporary **Inbox** storage (Redis/Kafka) until user reconnects, then sync to DB.

---

## 🏗️ System Architecture

1.  **Chat Server (WebSocket Gateway)**:
    *   Maintains persistent WS connections with users.
    *   Stateful service (Needs sticky sessions or a distributed session manager).
2.  **Service Discovery (Zookeeper/Etcd)**:
    *   Tracks which Chat Server holds User A's connection.
    *   Map: `User_A` -> `Server_IP_1`.
3.  **Message Service (API)**:
    *   Receives message from sender's Chat Server.
    *   Writes to **Cassandra**.
    *   Finds receiver's Chat Server (via Redis/Service Discovery) and pushes content.
4.  **Group Chat Service**:
    *   Fan-out service. If A sends to Group G (Members A, B, C):
    *   Lookup members of G.
    *   Push to B's Chat Server and C's Chat Server.
5.  **Presence Service**:
    *   Heartbeat mechanism.
    *   User sends heartbeat every 5s.
    *   Update Status in Redis with TTL = 10s.

---

## 💻 Code Simulation: Message Routing

Simulating the core logic of a Chat Server handling connections and offline queuing.

```python
import time

class ChatServer:
    def __init__(self):
        # Mocking active WebSocket connections: user_id -> connection_object
        self.active_connections = {}
        # Mocking Database: user_id -> list of messages
        self.message_store = {}
        # Offline Queue (for push notifications later, simplified here)
        self.offline_queue = {}

    def connect(self, user_id):
        print(f"🔌 User {user_id} connected.")
        self.active_connections[user_id] = True
        # Deliver offline messages
        if user_id in self.offline_queue:
            msgs = self.offline_queue.pop(user_id)
            for msg in msgs:
                print(f"   📨 [Deferred Delivery] To {user_id}: {msg}")

    def disconnect(self, user_id):
        print(f"❌ User {user_id} disconnected.")
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    def send_message(self, sender_id, receiver_id, content):
        timestamp = time.time()
        msg_obj = {"from": sender_id, "content": content, "ts": timestamp}

        # 1. Persist Message (Write-ahead)
        if receiver_id not in self.message_store:
            self.message_store[receiver_id] = []
        self.message_store[receiver_id].append(msg_obj)
        print(f"💾 DB: Saved message from {sender_id} to {receiver_id}")

        # 2. Try to deliver via WebSocket
        if receiver_id in self.active_connections:
            print(f"   🚀 [WebSocket] Pushed to {receiver_id}: {content}")
        else:
            print(f"   💤 User {receiver_id} offline. Queued.")
            if receiver_id not in self.offline_queue:
                self.offline_queue[receiver_id] = []
            self.offline_queue[receiver_id].append(msg_obj)

if __name__ == "__main__":
    chat = ChatServer()

    # User A connects
    chat.connect("Alice")

    # Alice sends to Bob (Offline)
    chat.send_message("Alice", "Bob", "Hi Bob! Are you there?")

    # Bob connects
    chat.connect("Bob")

    # Bob replies
    chat.send_message("Bob", "Alice", "Hey Alice! I'm here now.")
```

**Output:**
```
🔌 User Alice connected.
💾 DB: Saved message from Alice to Bob
   💤 User Bob offline. Queued.
🔌 User Bob connected.
   📨 [Deferred Delivery] To Bob: {'from': 'Alice', 'content': 'Hi Bob! Are you there?', 'ts': ...}
💾 DB: Saved message from Bob to Alice
   🚀 [WebSocket] Pushed to Alice: Hey Alice! I'm here now.
```

---

## 🧠 Interview Nuances

### 1. How to handle Group Chats?
*   **Small Groups (WhatsApp)**: Client-side fanout or Server-side "light" fanout. Messages are stored per user inbox.
*   **Mega Groups (Discord/Slack)**: Store message once in "Channel" Timeline. Users pull from channel timeline. Fanout on write is too expensive for 100k users.

### 2. How to ensure message ordering?
*   Use a **Sequence Number** or **Timestamp** generator (Snowflake ID) at the server side.
*   Client re-sorts messages based on ID if they arrive out of order.

### 3. Last Seen / Online Status?
*   Do not write to DB every second.
*   Use **Redis** with TTL.
*   `SET user:123:status "Online" EX 10`
*   If heartbeat stops, key expires -> User is Offline.

---

## ⚡ Flashcards
1.  **WebSocket vs HTTP Long Polling?**
    *   WebSocket is full-duplex (2-way), lower overhead. Long polling opens/closes connections repeatedly.
2.  **Why Cassandra for Chat?**
    *   Extremely high write throughput, good for time-series data (Chat History), linear scalability.
3.  **What is the "Fan-out" problem in Group Chat?**
    *   Sending 1 message to a group of 1M users means generating 1M distinct writes/notifications, causing a storm.
