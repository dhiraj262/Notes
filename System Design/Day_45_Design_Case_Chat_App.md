# Day 45: Design Case - Chat App (WhatsApp/Telegram)

## 🎯 Goal
Design a real-time chat application like WhatsApp or Facebook Messenger.
**Focus**: Real-time communication (WebSockets), Scale (Billions of messages), and Consistency (Ordering).

---

## 🗣️ Requirements

### Functional
1.  **One-on-One Chat**: Send text, images between two users.
2.  **Sent/Delivered/Read Receipts**: Status updates for messages.
3.  **Online/Offline Status**: Show if user is online.
4.  **Persistent Chat History**: Messages are stored forever.

### Non-Functional
1.  **Low Latency**: Real-time delivery (< 500ms).
2.  **High Availability**: System should not go down.
3.  **Consistency**: Messages must be ordered correctly (Causal ordering).

---

## 📐 Capacity Estimation
*   **DAU**: 500 Million.
*   **Msgs/Day**: 500M * 40 = 20 Billion messages/day.
*   **Storage**: 20B * 100 bytes = 2TB/day. (Cassandra/HBase required).
*   **Bandwidth**: Heavy due to media.

---

## 🧠 Core Design Decisions

### 1. Protocol: HTTP vs WebSocket
*   **HTTP**: Request-Response. Client must poll "Any new messages?". Inefficient (Long Polling).
*   **WebSocket**: Persistent, bi-directional connection. Server pushes messages to client instantly.
    *   **Decision**: Use **WebSockets** for real-time delivery.

### 2. Database: SQL vs NoSQL
*   **SQL (MySQL)**: Good for ACID, but hard to scale for 20B writes/day. Hard to partition efficiently for infinite history.
*   **NoSQL (Cassandra/HBase)**: Wide-column stores. Optimized for write throughput.
    *   **Schema**: `PartitionKey: ChatID`, `ClusteringKey: MessageID (Timestamp)`. Efficient range queries (fetch last 50 msgs).

### 3. Message Ordering
*   Can't rely on server wall-clock (clock skew).
*   Use a distributed sequence generator (Snowflake ID) which is roughly sortable by time.

---

## 🏗️ System Architecture

1.  **Chat Service (WebSocket)**: Holds persistent connections. Stateful.
    *   Map: `UserID -> ConnectionObj`.
2.  **Presence Service**: Tracks Online/Offline status.
    *   Uses **Redis** with Heartbeats. Client pings every 10s. If missed -> Offline.
3.  **Message Service**:
    *   Receives message from User A.
    *   Writes to **Cassandra**.
    *   Checks Redis for User B's "Chat Service" server address.
    *   Forwards message to that server -> Pushes to User B.
    *   If User B offline -> Push Notification Service.

---

## 💻 Code Simulation: Message Flow

Simulating the core logic of handling online vs offline delivery.

```python
import time
import queue

class ChatSystem:
    def __init__(self):
        self.sessions = {} # user_id -> status (Online/Offline)
        self.messages_db = [] # Log of all messages
        self.offline_queue = {} # user_id -> [messages]

    def connect(self, user_id):
        self.sessions[user_id] = "ONLINE"
        print(f"✅ User {user_id} connected.")
        # Deliver offline messages
        if user_id in self.offline_queue:
            for msg in self.offline_queue[user_id]:
                print(f"   ↪️ Delivering offline msg to {user_id}: {msg}")
            del self.offline_queue[user_id]

    def disconnect(self, user_id):
        self.sessions[user_id] = "OFFLINE"
        print(f"❌ User {user_id} disconnected.")

    def send_message(self, sender, receiver, content):
        timestamp = time.time()
        msg_obj = {"from": sender, "to": receiver, "content": content, "ts": timestamp}

        # 1. Persist (Cassandra Style - Append Only)
        self.messages_db.append(msg_obj)
        print(f"💾 Message persisted: {sender} -> {receiver}")

        # 2. Check Receiver Status (Redis Style)
        status = self.sessions.get(receiver, "OFFLINE")

        if status == "ONLINE":
            # 3. Deliver via WebSocket
            print(f"   🚀 Delivered to {receiver}: {content}")
        else:
            # 4. Queue for later
            if receiver not in self.offline_queue:
                self.offline_queue[receiver] = []
            self.offline_queue[receiver].append(content)
            print(f"   💤 User {receiver} is Offline. Queued.")

if __name__ == "__main__":
    whatsapp = ChatSystem()

    # 1. User A connects
    whatsapp.connect("Alice")

    # 2. User A sends to B (who is offline)
    whatsapp.send_message("Alice", "Bob", "Hello Bob!")

    # 3. Bob connects
    whatsapp.connect("Bob")

    # 4. Bob replies
    whatsapp.send_message("Bob", "Alice", "Hi Alice!")
```

**Output:**
```
✅ User Alice connected.
💾 Message persisted: Alice -> Bob
   💤 User Bob is Offline. Queued.
✅ User Bob connected.
   ↪️ Delivering offline msg to Bob: Hello Bob!
💾 Message persisted: Bob -> Alice
   🚀 Delivered to Alice: Hi Alice!
```

---

## 🧠 Interview Nuances

### 1. Group Chat?
*   Complexity explodes.
*   **Read Amplification**: 1 sender, 500 receivers.
*   Design: Iterate group members, lookup their WebSocket servers, parallel push.
*   Limit group size (WhatsApp: 256/1024) to constrain fan-out.

### 2. End-to-End Encryption (E2EE)?
*   Server **cannot** store plain text.
*   Client A encrypts with Client B's Public Key. Only B can decrypt with Private Key.
*   Server only stores blobs. Search (Ctrl+F) is hard (must be done locally on device).

### 3. "Last Seen" feature?
*   Don't update DB on every heartbeat (too many writes).
*   Update Redis only. Persist to DB only on disconnect or every 5 mins.

---

## ⚡ Flashcards
1.  **WebSocket vs Long Polling?**
    *   WebSocket is full-duplex (server pushes). Long Polling is a hack (client asks and waits).
2.  **Why Cassandra for Chat?**
    *   Extreme write throughput + Time-series data model fits chat history perfectly.
3.  **What is a "Fan-out"?**
    *   One message triggering multiple deliveries (e.g., Group chat, Twitter feed).
