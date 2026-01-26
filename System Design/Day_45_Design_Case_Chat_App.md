# Day 45: Design Case - Chat App (WhatsApp/Slack)

## 🎯 Goal
Design a scalable chat application that supports 1-on-1 messaging, group chats, online presence, and read receipts.
**Focus**: Real-time communication, High Write Throughput, and Consistency.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Low latency delivery.
2.  **Group Chat**: Up to 256 members.
3.  **Receipts**: Sent (Server), Delivered (User Device), Read (User Opened).
4.  **Online/Offline Status**: Last seen.
5.  **Media**: Support images/videos (Metadata in DB, Blob in S3).

### Non-Functional
1.  **Low Latency**: Real-time experience (< 100ms).
2.  **High Availability**: Chat must always work.
3.  **Consistency**: Messages must appear in order.
4.  **Durability**: Messages should never be lost once acknowledged.

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million Users.
*   **Messages**: 50 per user/day -> 5 Billion messages/day.
*   **Storage**: 5B * 100 Bytes = 500 GB/day. **180 TB/year**.
*   **QPS**: 5B / 86400 ≈ 57k msg/sec. Peak (x5) ≈ **300k msg/sec**.
*   **Bandwidth**: Media heavily increases this.

---

## 🧠 Core Design Decisions

### 1. Connection: HTTP vs WebSockets
*   **HTTP (Long Polling)**: Client keeps asking "Any new messages?". Inefficient for high throughput.
*   **WebSockets**: Bi-directional persistent connection. Server pushes messages to client instantly.
    *   **Decision**: Use **WebSockets** for active sessions. Use Push Notifications (FCM/APNS) for offline users.

### 2. Database: SQL vs NoSQL
*   **Pattern**: Very high write volume. Access pattern is "Load recent messages for Chat X".
*   **SQL (MySQL/Postgres)**: Hard to scale writes to 5B/day without complex sharding.
*   **NoSQL (Cassandra/HBase)**: LSM-tree based. Optimised for heavy writes.
    *   **Decision**: **Cassandra**.
    *   **Partition Key**: `chat_id` (Stores all messages for a chat together).
    *   **Clustering Key**: `timestamp` (Sorts messages by time).

### 3. Service Discovery & Session Management
*   User A is connected to Server 1. User B is connected to Server 2.
*   How does Server 1 know where to send User A's message for User B?
*   **Solution**: **Session Service** (Redis).
    *   Key: `user_id` -> Value: `gateway_server_ip`.

---

## 🏗️ System Architecture

1.  **WebSocket Handler (Gateway)**: Holds persistent connections.
2.  **Chat Service**: Orchestrates logic. Saves to DB.
3.  **Session Service (Redis)**: Tracks which Gateway node a user is connected to.
4.  **Cassandra**: Stores message history (`chat_messages`).
5.  **Group Service**: Manages group memberships.
6.  **Push Service**: If user is offline, send via FCM/APNS.

**Flow (User A sends to User B):**
1.  User A sends msg to `Gateway-1` via WebSocket.
2.  `Gateway-1` calls `Chat Service`.
3.  `Chat Service` persists msg to `Cassandra`.
4.  `Chat Service` queries `Session Service` (Redis) to find User B.
    *   **Scenario 1: User B Online on Gateway-2**: `Chat Service` forwards msg to `Gateway-2`, which pushes to User B.
    *   **Scenario 2: User B Offline**: `Chat Service` triggers `Push Service`.

---

## 💻 Code Simulation: Message Routing

Simulating the core routing logic between users connected to different servers.

```python
import time
import queue
import threading

class SessionStore:
    """Mock Redis Session Store"""
    def __init__(self):
        self.sessions = {} # user_id -> server_id

    def set_user_server(self, user_id, server_id):
        self.sessions[user_id] = server_id

    def get_user_server(self, user_id):
        return self.sessions.get(user_id)

class GatewayServer:
    """Simulates a WebSocket Server handling user connections"""
    def __init__(self, server_id, central_router):
        self.server_id = server_id
        self.router = central_router
        self.connected_users = {} # user_id -> socket (queue)

    def connect(self, user_id):
        print(f"🔌 [{self.server_id}] User {user_id} connected")
        self.connected_users[user_id] = queue.Queue()
        self.router.register_session(user_id, self.server_id)
        # Start listening for messages for this user
        threading.Thread(target=self._listen_to_client, args=(user_id,), daemon=True).start()

    def send_message(self, from_user, to_user, content):
        print(f"📤 [{self.server_id}] User {from_user} sending to {to_user}: {content}")
        self.router.route_message(from_user, to_user, content)

    def receive_message(self, user_id, message):
        """Called by Router when a message arrives for a user on this server"""
        if user_id in self.connected_users:
            print(f"📩 [{self.server_id}] Delivering to User {user_id}: {message}")
            self.connected_users[user_id].put(message)

    def _listen_to_client(self, user_id):
        # Simulating receiving messages loop
        pass

class CentralRouter:
    """Simulates Chat Service + Session Lookup"""
    def __init__(self):
        self.session_store = SessionStore()
        self.servers = {}

    def add_server(self, server):
        self.servers[server.server_id] = server

    def register_session(self, user_id, server_id):
        self.session_store.set_user_server(user_id, server_id)

    def route_message(self, from_user, to_user, content):
        # 1. Save to DB (Mock)
        # 2. Find Recipient
        target_server_id = self.session_store.get_user_server(to_user)

        if target_server_id and target_server_id in self.servers:
             # User is Online
             self.servers[target_server_id].receive_message(to_user, f"From {from_user}: {content}")
        else:
             # User is Offline -> Push Notification
             print(f"📳 [Push Service] User {to_user} is offline. Sending Push: {content}")

if __name__ == "__main__":
    router = CentralRouter()

    # Init Servers
    gw1 = GatewayServer("GW-01", router)
    gw2 = GatewayServer("GW-02", router)
    router.add_server(gw1)
    router.add_server(gw2)

    # Users Connect
    gw1.connect("Alice")   # Alice on Server 1
    gw2.connect("Bob")     # Bob on Server 2

    time.sleep(1)

    # Communication
    gw1.send_message("Alice", "Bob", "Hello Bob!")
    gw2.send_message("Bob", "Alice", "Hi Alice, how are you?")

    # Offline Scenario
    gw1.send_message("Alice", "Charlie", "Are you there?")
```

**Output:**
```
🔌 [GW-01] User Alice connected
🔌 [GW-02] User Bob connected
📤 [GW-01] User Alice sending to Bob: Hello Bob!
📩 [GW-02] Delivering to User Bob: From Alice: Hello Bob!
📤 [GW-02] User Bob sending to Alice: Hi Alice, how are you?
📩 [GW-01] Delivering to User Alice: From Bob: Hi Alice, how are you?
📤 [GW-01] User Alice sending to Charlie: Are you there?
📳 [Push Service] User Charlie is offline. Sending Push: Are you there?
```

---

## 🧠 Interview Nuances

### 1. How to handle Group Chats?
*   **Fan-out on Write** (Limit group size ~200): Sender sends 1 msg. Server copies it into the Inbox of all 200 members. Fast reads.
*   **Fan-out on Read** (Large channels ~1M): Sender writes 1 msg. Users pull from the Group timeline.
*   **Hybrid**: WhatsApp uses Fan-out on Write because groups are small.

### 2. Message Ordering
*   Within a single chat, messages must be ordered.
*   Use `Sequence ID` or `Snowflake ID` generated by the server.
*   Cassandra sorts columns by `timestamp` automatically.

### 3. "Sent" vs "Delivered"
*   **Sent**: Server received msg. (Ack to Sender).
*   **Delivered**: Recipient's WebSocket sent an ACK back to Server. Server updates Sender.
*   **Read**: Recipient opened the chat UI. App sends "Read" event.

---

## ⚡ Flashcards
1.  **Why WebSocket over HTTP?**
    *   Lower overhead (header compression), bi-directional, lower latency for real-time interaction.
2.  **Why Cassandra for Chat?**
    *   Excellent write throughput. Data model (Partition by ChatID) fits "Get all messages for this chat" perfectly.
3.  **What is the "Thundering Herd" problem?**
    *   If a Gateway crashes, 1M users try to reconnect instantly. **Solution**: Add random jitter (backoff) to client reconnection logic.
