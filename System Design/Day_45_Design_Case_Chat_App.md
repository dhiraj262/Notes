# Day 45: Design Case - Chat App (WhatsApp/Telegram)

## 🎯 Goal
Design a massive scale chat application that supports 1-on-1 chat, group chat, and online presence indicators.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Low latency delivery.
2.  **Group Chat**: Up to 256 members.
3.  **Online Status**: Sent/Delivered/Read receipts.
4.  **Media Sharing**: Images/Videos (handled via Blob storage, not covered in deep detail here).
5.  **Multi-device Support**: Messages synced across phone and web.

### Non-Functional
1.  **Low Latency**: Real-time experience (< 100ms).
2.  **High Availability**: Chat must never go down.
3.  **Consistency**: Messages must be ordered (Causal consistency).

---

## 📐 Capacity Estimation
*   **DAU**: 500 Million.
*   **Messages/Day**: 40 per user -> 20 Billion msgs/day.
*   **Storage**: 20B * 50 bytes = 1 TB/day. 5 Years = ~1.8 PB.
*   **Bandwidth**: Peak traffic management is key.

---

## 🧠 Core Design Decisions

### 1. Protocol: HTTP vs WebSockets
*   **HTTP**: Request/Response. Bad for "server pushing" messages to client. Polling is inefficient.
*   **WebSockets**: Bi-directional, persistent connection. Ideal for chat.
*   **Decision**: Use **WebSockets** for sending/receiving messages. Use **HTTP/REST** for file uploads, profile updates, and authentication.

### 2. Database: SQL vs NoSQL
*   We need extremely high write throughput and simple key-value lookups (Get history for Chat ID).
*   **RDBMS (MySQL/Postgres)**: Hard to scale writes for 20B/day.
*   **NoSQL (Cassandra/HBase)**: Wide-column stores are perfect for time-series chat logs.
*   **Decision**: **Cassandra** (or ScyllaDB). Partition Key: `chat_id`, Clustering Key: `timestamp`.

### 3. Message ID Generation
*   Need global unique ordering? No, only ordering *within* a chat matters.
*   Can use `Snowflake ID` (64-bit sortable ID) or a local counter per chat.

---

## 🏗️ System Architecture

1.  **Chat Service (WebSocket Server)**:
    *   Maintains open connections with online users.
    *   Stateful (needs to know which server holds User A's connection).
    *   Managed by **Zookeeper/Redis** to map `User_ID -> Gateway_Server_IP`.

2.  **Message Routing**:
    *   User A sends msg to User B.
    *   Server A checks Redis: "Where is User B?"
    *   If Online (Server B): Forward msg to Server B -> Push to User B.
    *   If Offline: Write to **Cassandra**.
    *   If Group: Fan-out service expands GroupID -> List[UserIDs].

3.  **Presence Service**:
    *   Heartbeat mechanism. Client sends "I'm alive" every 5s.
    *   Stored in **Redis** with TTL.

---

## 💻 Code Simulation: Message Router

Simulates the routing logic for Online vs Offline users.

```python
import queue
import threading
import time

class ChatSystem:
    def __init__(self):
        # mock_db stores messages for offline users: {user_id: [msg1, msg2]}
        self.offline_storage = {}
        # active_sessions stores "connections": {user_id: queue}
        self.active_sessions = {}
        self.lock = threading.Lock()

    def connect(self, user_id):
        with self.lock:
            self.active_sessions[user_id] = queue.Queue()
            print(f"✅ User {user_id} connected (Online)")

            # Flush offline messages
            if user_id in self.offline_storage:
                msgs = self.offline_storage.pop(user_id)
                print(f"   📬 Flushing {len(msgs)} offline messages to {user_id}")
                for msg in msgs:
                    self.active_sessions[user_id].put(msg)

    def disconnect(self, user_id):
        with self.lock:
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
                print(f"❌ User {user_id} disconnected (Offline)")

    def send_message(self, from_user, to_user, content):
        timestamp = time.strftime('%H:%M:%S')
        message = {"from": from_user, "content": content, "time": timestamp}

        with self.lock:
            if to_user in self.active_sessions:
                # User is online, push to their queue (WebSocket)
                print(f"📨 Routing: {from_user} -> {to_user}: {content}")
                self.active_sessions[to_user].put(message)
            else:
                # User is offline, store in DB
                print(f"💾 Storing: {from_user} -> {to_user} (Offline)")
                if to_user not in self.offline_storage:
                    self.offline_storage[to_user] = []
                self.offline_storage[to_user].append(message)

    def receive_loop(self, user_id):
        """Simulates the client receiving messages via WebSocket"""
        while True:
            # Check if user is still connected
            if user_id not in self.active_sessions:
                break

            try:
                # Get message from their queue
                q = self.active_sessions[user_id]
                msg = q.get(timeout=0.5)
                print(f"   👀 Client {user_id} received: '{msg['content']}' from {msg['from']}")
            except queue.Empty:
                continue

# Simulation usage
if __name__ == "__main__":
    chat = ChatSystem()
    chat.connect("Alice")

    t_alice = threading.Thread(target=chat.receive_loop, args=("Alice",))
    t_alice.start()

    # Online
    chat.send_message("Bob", "Alice", "Hello Alice!")
    time.sleep(1)

    # Offline
    chat.disconnect("Alice")
    t_alice.join()
    chat.send_message("Bob", "Alice", "Are you there?")

    # Reconnect
    chat.connect("Alice")
    t_alice_reconnect = threading.Thread(target=chat.receive_loop, args=("Alice",))
    t_alice_reconnect.start()
    time.sleep(1)
    chat.disconnect("Alice")
    t_alice_reconnect.join()
```

---

## 🧠 Interview Nuances

### 1. How to handle Group Chat fan-out?
*   **Small Group (WhatsApp)**: Client-side or Server-side loop. Sending to 10 people is fast.
*   **Large Channel (Telegram/Discord)**: Kafka is needed.
    *   Producer pushes "New Msg in Channel X" to Kafka.
    *   Workers read, fetch subscribers, and push to their connected WebSocket servers.

### 2. Sent vs Delivered vs Read
*   **Sent**: Client -> Server (Ack).
*   **Delivered**: Server -> Recipient (Ack from Recipient's device).
*   **Read**: Recipient opens chat -> Sends "Read Event" to Server -> Forward to Sender.

---

## ⚡ Flashcards
1.  **Why WebSocket over HTTP for chat?**
    *   Lower overhead (header compression), persistent connection, real-time push capability.
2.  **What is Long Polling?**
    *   Client asks "Any new msg?". Server holds request open until a msg arrives or timeout. Better than short polling, worse than WebSockets.
3.  **Why Cassandra for chat history?**
    *   Excellent write speed (LSM Tree) and efficient range queries (fetch all msgs for `chat_id` ordered by time).
