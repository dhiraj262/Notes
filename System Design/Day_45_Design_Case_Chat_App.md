# Day 45: Design Case - Chat App (WhatsApp/Slack)

## 🎯 Goal
Design a real-time chat application similar to WhatsApp or Slack.
**Focus**: Real-time delivery, Message storage, and Online/Offline status.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Low latency delivery.
2.  **Group Chat**: Support groups with up to 256 members.
3.  **Delivery Status**: Sent (1 tick), Delivered (2 ticks), Read (Blue ticks).
4.  **Media**: Support Image/Video sharing.
5.  **Online Status**: Show if user is "Online" or "Last seen at...".

### Non-Functional
1.  **Low Latency**: Real-time experience (< 100ms).
2.  **High Availability**: Always accept messages.
3.  **Consistency**: Messages must appear in order (FIFO).
4.  **Scale**: 2 Billion users.

---

## 📐 Capacity Estimation
*   **DAU**: 100 Million active users.
*   **Messages**: 20 per user/day -> 2 Billion messages/day.
*   **Throughput**: 2B / 86400 ≈ **23,000 msg/sec** (Average). Peak ~100k/sec.
*   **Storage**: 2B * 100 Bytes = 200 GB/day.
    *   5 Years: 200GB * 365 * 5 ≈ 365 PB (Need massive storage -> Blob + Metadata).
*   **Bandwidth**: If 10% msgs are media (1MB), bandwidth is huge.

---

## 🧠 Core Design Decisions

### 1. Protocol: WebSockets vs HTTP
*   **HTTP**: Request/Response. Bad for receiving messages (Server needs to Push). Polling is expensive.
*   **WebSockets**: Persistent bi-directional connection. Server can push message to client instantly.
*   **Decision**: Use **WebSockets** for active chats. Use Push Notifications (FCM) when user is offline.

### 2. Database for Chat History
*   **RDBMS (MySQL)**: Good for relations, but hard to scale for 200GB/day writes.
*   **NoSQL (Cassandra/HBase)**:
    *   Key-Value/Wide-Column stores.
    *   Excellent Write throughput (LSM Trees).
    *   Query pattern: `Get messages where channel_id = X AND timestamp > Y`.
    *   **Decision**: **Cassandra** or **HBase** (Pattern used by Discord/Facebook).

### 3. Handling Group Chats
*   **Fan-out on Write**: When A sends message to Group G (Users B, C, D), Server copies message to Inbox B, Inbox C, Inbox D. (Good for small groups).
*   **Fan-out on Read**: Store 1 copy in "Group Channel". Users pull from there. (Good for huge channels like Slack).
*   **Decision**: WhatsApp uses Client-Side Fan-out (mostly) or Hybrid. For us, Server-Side Fan-out for small groups (< 200).

---

## 🏗️ System Architecture

1.  **Chat Service (WebSocket Server)**: Maintains persistent connections. Statefull.
    *   Maps `User_ID` -> `Connection_Object`.
2.  **Service Discovery (Zookeeper/Redis)**: Keeps track of which Chat Server holds User A's connection.
3.  **Message Service**: API to ingest messages, persist to DB, and route to receiver.
4.  **Presence Service**: Heartbeat mechanism to update "Last Seen".
5.  **Asset Service**: Stores media in S3/Blob Store, stores URL in Chat DB.

**Flow (User A sends to User B):**
1.  User A sends msg via WebSocket to Chat Server 1.
2.  Chat Server 1 calls Message Service.
3.  Message Service:
    *   Saves to **Cassandra**.
    *   Queries **Redis** to find which Chat Server User B is connected to (say, Server 2).
    *   Forwards message to Chat Server 2.
4.  Chat Server 2 pushes msg via WebSocket to User B.
5.  If User B is offline -> Send to **Push Notification Service**.

---

## 💻 Code Simulation: Pub-Sub Message Routing

```python
import threading
import time
import collections

class ChatServer:
    def __init__(self, server_id):
        self.server_id = server_id
        self.connections = {} # UserID -> Queue (Mocking WebSocket)
        self.lock = threading.Lock()

    def connect(self, user_id):
        with self.lock:
            self.connections[user_id] = []
            print(f"✅ User {user_id} connected to Server {self.server_id}")

    def send_message(self, user_id, message):
        with self.lock:
            if user_id in self.connections:
                self.connections[user_id].append(message)
                print(f"   🚀 [Server {self.server_id}] Pushing to {user_id}: {message}")
                return True
            else:
                return False # User not on this server

class Router:
    def __init__(self):
        self.user_server_map = {} # Redis: UserID -> ServerID
        self.servers = {}

    def register_user(self, user_id, server):
        self.user_server_map[user_id] = server.server_id
        self.servers[server.server_id] = server
        server.connect(user_id)

    def route_message(self, from_user, to_user, text):
        server_id = self.user_server_map.get(to_user)
        if not server_id:
            print(f"   zzz User {to_user} is Offline. Sending Push Notification.")
            return

        server = self.servers[server_id]
        print(f"📨 Routing msg from {from_user} to {to_user} via Server {server_id}")
        server.send_message(to_user, f"From {from_user}: {text}")

if __name__ == "__main__":
    router = Router()
    s1 = ChatServer(1)
    s2 = ChatServer(2)

    # Users connect
    router.register_user("Alice", s1)
    router.register_user("Bob", s2)

    # Alice sends to Bob (Cross-Server)
    router.route_message("Alice", "Bob", "Hello Bob!")

    # Bob sends to Charlie (Offline)
    router.route_message("Bob", "Charlie", "Are you there?")
```

---

## 🧠 Interview Nuances

### 1. How to maintain message ordering?
*   Use a sequence generator (like Snowflake) to generate sortable Message IDs.
*   Within a conversation, the client can re-order based on ID if packets arrive out of order.

### 2. How to handle "Last Seen" efficiently?
*   Don't write to DB on every heartbeat (too many writes).
*   Update Redis every heartbeat (TTL 30s).
*   Only flush to persistent DB when user disconnects or every 5 mins.

### 3. End-to-End Encryption (E2EE)?
*   The server stores encrypted blobs. It cannot read the messages.
*   Keys are exchanged between Alice and Bob (Signal Protocol/Double Ratchet).

---

## ⚡ Flashcards
1.  **Why Cassandra for Chat?**
    *   Huge write throughput (LSM Tree) and efficient range queries (Fetch history).
2.  **WebSocket vs Server-Sent Events (SSE)?**
    *   WebSocket is bi-directional (Chat). SSE is server-to-client only (Stock Ticker).
3.  **What is a Heartbeat?**
    *   Periodic signal (e.g., every 5s) sent by client to server to say "I am alive/online".
