# Day 45: Design Case - Chat App (WhatsApp/Telegram)

## 🎯 Goal
Design a scalable real-time chat application like WhatsApp or Telegram supporting 1-on-1 and Group chats for 500 Million daily active users.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Low latency messaging.
2.  **Group Chat**: Support groups with up to 256 members.
3.  **Receipts**: Sent (Single tick), Delivered (Double tick), Read (Blue tick).
4.  **Online Status**: Last seen / Online.
5.  **Media**: Support images/videos (handled via Blob storage, we focus on text/metadata here).

### Non-Functional
1.  **Real-time**: Latency < 100ms.
2.  **Consistency**: Messages must be ordered (Causal consistency).
3.  **Availability**: High availability for sending messages (Partition Tolerance over Consistency if needed, but chat usually prefers Consistency within a session).
4.  **Durability**: Messages should never be lost once sent.

---

## 📐 Capacity Estimation
*   **DAU**: 500 Million.
*   **Msgs/User/Day**: 40.
*   **Total Messages**: 500M * 40 = 20 Billion msgs/day.
*   **Traffic**: 20B / 86400 ≈ 230,000 msg/sec. Peak 1M msg/sec.
*   **Storage**:
    *   Avg msg size = 50 bytes.
    *   20B * 50B = 1TB/day.
    *   5 Years = ~1.8 PB. (Requires a highly scalable DB like HBase/Cassandra).

---

## 🧠 Core Design Decisions

### 1. Communication Protocol: WebSocket
*   **HTTP/REST**: Too slow (opening new connection for every message). Overhead of headers.
*   **Long Polling**: Better, but server holds connection.
*   **WebSocket**: Best. Bi-directional, persistent connection. Server can push messages to client instantly.

### 2. Database: Wide-Column Store (Cassandra/HBase)
*   **Pattern**: Write-heavy (1:1 Read/Write ratio or even higher writes).
*   **Why NoSQL**: relational DBs struggle with TBs of new data daily.
*   **Schema**:
    *   `Partition Key`: `chat_id` (Keeps all messages for a chat together).
    *   `Clustering Key`: `message_id` (Snowflake ID, sort by time).
    *   This allows O(1) fetch of "last 50 messages".

### 3. Service Discovery
*   User A is connected to Server 1. User B is connected to Server 2.
*   How does Server 1 know where to send the message?
*   **Session Service** (Redis/Zookeeper): Maintains a map `User_ID -> Gateway_Server_IP`.

---

## 🏗️ System Architecture

1.  **Chat Service (Stateful)**: Maintains WebSocket connections.
2.  **Service Discovery (Zookeeper/Redis)**: Maps Users to Chat Servers.
3.  **Message Service (Stateless API)**: Handles auth, saving message to DB, and routing.
4.  **Group Message Handler**:
    *   If Group has 200 users, expand the message into 200 individual pushes?
    *   Optimization: Write once to "Group Inbox", notify members to pull? Or Hybrid.
    *   For WhatsApp (small groups): Fan-out on write (push to all queues) is usually fine.
5.  **Push Notification Service**: If user is offline (no WebSocket), send via FCM/APNS.

---

## 💻 Code Simulation: Chat Server Logic

Simulating the core logic of handling connections and routing messages between users (Online vs Offline).

```python
import threading
import queue

class ChatServer:
    def __init__(self):
        # Maps user_id -> Queue (representing a WebSocket connection)
        self.active_sessions = {}
        self.lock = threading.Lock()
        self.offline_messages = {} # Mock DB for offline msgs

    def connect(self, user_id):
        """Simulates a user connecting via WebSocket"""
        with self.lock:
            self.active_sessions[user_id] = queue.Queue()
            print(f"✅ User {user_id} Connected")
        return self.active_sessions[user_id]

    def disconnect(self, user_id):
        with self.lock:
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
                print(f"❌ User {user_id} Disconnected")

    def send_message(self, sender_id, receiver_id, content):
        """Routes message to receiver or stores if offline"""
        print(f"📩 {sender_id} -> {receiver_id}: {content}")

        with self.lock:
            if receiver_id in self.active_sessions:
                # Online: Push to socket
                user_queue = self.active_sessions[receiver_id]
                user_queue.put(f"From {sender_id}: {content}")
                print(f"   🚀 Pushed to User {receiver_id}'s socket")
            else:
                # Offline: Store in DB
                if receiver_id not in self.offline_messages:
                    self.offline_messages[receiver_id] = []
                self.offline_messages[receiver_id].append(f"From {sender_id}: {content}")
                print(f"   💾 User {receiver_id} Offline. Saved to DB.")

    def receive_loop(self, user_id):
        """Simulates Client listening on the socket"""
        if user_id not in self.active_sessions:
            return

        q = self.active_sessions[user_id]
        while True:
            try:
                # Check for new messages
                msg = q.get(timeout=0.5)
                print(f"   📱 Client {user_id} received: '{msg}'")
            except queue.Empty:
                break # Just for simulation, exit loop

if __name__ == "__main__":
    server = ChatServer()

    # 1. User A and B connect
    server.connect("Alice")
    server.connect("Bob")

    # 2. Alice sends to Bob (Online)
    server.send_message("Alice", "Bob", "Hello Bob!")

    # 3. Simulate Bob receiving
    server.receive_loop("Bob")

    # 4. Bob disconnects
    server.disconnect("Bob")

    # 5. Alice sends to Bob (Offline)
    server.send_message("Alice", "Bob", "Are you there?")

    # 6. Bob reconnects and fetches offline (Simulation of logic)
    server.connect("Bob")
    stored_msgs = server.offline_messages.get("Bob", [])
    for msg in stored_msgs:
        print(f"   🔄 [Sync] Client Bob fetched: '{msg}'")
```

**Output:**
```
✅ User Alice Connected
✅ User Bob Connected
📩 Alice -> Bob: Hello Bob!
   🚀 Pushed to User Bob's socket
   📱 Client Bob received: 'From Alice: Hello Bob!'
❌ User Bob Disconnected
📩 Alice -> Bob: Are you there?
   💾 User Bob Offline. Saved to DB.
✅ User Bob Connected
   🔄 [Sync] Client Bob fetched: 'From Alice: Are you there?'
```

---

## 🧠 Interview Nuances

### 1. How to handle "Last Seen"?
*   **Heartbeat**: Client sends a heartbeat every 5 seconds.
*   Redis stores `last_active_time`.
*   If `current_time - last_active > 10s`, show "Offline".

### 2. How to ensure Message Ordering?
*   Use a **Sequence Generator** (Snowflake ID) which is time-sortable.
*   On the client side, if msg 5 arrives before msg 4, wait/buffer until 4 arrives (TCP handles this mostly, but app logic might need to handle gaps if using UDP/custom).

### 3. What if the Chat Server dies?
*   The WebSocket breaks. Client auto-reconnects.
*   LB routes to a healthy server.
*   Service Discovery updates the mapping.

---

## ⚡ Flashcards
1.  **WebSocket vs HTTP for Chat?**
    *   WebSocket is persistent, full-duplex, low overhead. HTTP is request-response, high overhead.
2.  **Why HBase/Cassandra for Chat?**
    *   Extreme write throughput (millions/sec) and simple query patterns (Get messages by ChatID).
3.  **Fan-out on Read vs Write?**
    *   For small groups (WhatsApp), Fan-out on Write (deliver to all) is faster. For huge channels (Slack/Discord), Fan-out on Read (pull from channel) is better.
