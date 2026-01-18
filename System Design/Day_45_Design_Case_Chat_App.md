# Day 45: Design Case - Chat App (WhatsApp/Telegram)

## 🎯 Goal
Design a large-scale chat application supporting 1-on-1 and Group chats.
**Focus**: Real-time communication (Low Latency), Consistency (Message Ordering), and Online Status.

---

## 🗣️ Requirements

### Functional
1.  **1-on-1 Chat**: Send text, images, videos.
2.  **Group Chat**: Up to 256 members.
3.  **Delivery Status**: Sent (single tick), Delivered (double tick), Read (blue tick).
4.  **Online Status**: Show when a user was last active.
5.  **Multi-Device Support**: Sync messages across phone and web.

### Non-Functional
1.  **Low Latency**: Real-time delivery (< 500ms).
2.  **Consistency**: Messages must appear in order.
3.  **High Availability**: Always writeable.
4.  **Security**: End-to-End Encryption (E2EE).

---

## 📐 Capacity Estimation
*   **DAU**: 500 Million Users.
*   **Msgs/User**: 40 msgs/day -> 20 Billion msgs/day.
*   **QPS**: 20B / 86400 ≈ 230k msgs/sec. Peak ≈ 600k msgs/sec.
*   **Storage**:
    *   Avg msg size = 50 bytes.
    *   20B * 50B = 1TB/day of text. (Media is much larger, stored in S3).

---

## 🏗️ System Architecture

### 1. Connection Handling (WebSocket)
*   **Protocol**: WebSockets (Persistent connection) is better than HTTP Polling for real-time.
*   **Chat Server (Gateway)**: Maintains open WebSocket connections with active users.
    *   If User A sends msg to User B, Chat Server A finds which server holds User B's connection and routes it there.
    *   Uses **Redis/Zookeeper** to map `User_ID -> Gateway_Server_ID`.

### 2. Message Flow (1-on-1)
1.  **User A** sends msg to **Gateway A**.
2.  **Gateway A** writes to **Message Service**.
3.  **Message Service** saves to **Cassandra/HBase** (Write-heavy, Time-series).
4.  **Message Service** finds User B's gateway (via Redis/Service Discovery).
5.  **Gateway B** pushes msg to **User B**.
6.  If User B is offline, push to **Push Notification Service (FCM/APNS)**.

### 3. Group Chat
*   **Small Groups (< 500)**: Client-side fan-out is too expensive. Server-side fan-out.
*   **Message Service** looks up Group Members.
*   Iterates and pushes to each member's Gateway.

---

## 💻 Code Simulation: Routing Logic

Simulating the core logic of finding a user's connection and routing the message.

```python
import threading
import queue
import time

class ChatServer:
    def __init__(self):
        self.users = {} # user_id -> queue (simulating websocket)
        self.messages = [] # db

    def connect(self, user_id):
        self.users[user_id] = queue.Queue()
        print(f"✅ User {user_id} connected.")
        return self.users[user_id]

    def send_message(self, sender_id, receiver_id, content):
        msg = {"from": sender_id, "to": receiver_id, "content": content}
        self.messages.append(msg) # Save to DB

        if receiver_id in self.users:
            # User is online, push to their socket
            self.users[receiver_id].put(msg)
            print(f"   🚀 Pushed to {receiver_id}: {content}")
        else:
            # User is offline, push notif
            print(f"   💤 User {receiver_id} offline. Queued push notification.")

    def client_listener(self, user_id, q):
        start_time = time.time()
        while time.time() - start_time < 3: # Run for 3 seconds max
            try:
                msg = q.get(timeout=0.5)
                print(f"   📲 {user_id} received from {msg['from']}: {msg['content']}")
            except queue.Empty:
                continue

if __name__ == "__main__":
    server = ChatServer()

    # Alice and Bob connect
    alice_q = server.connect("Alice")
    bob_q = server.connect("Bob")

    # Start listeners
    t1 = threading.Thread(target=server.client_listener, args=("Alice", alice_q))
    t2 = threading.Thread(target=server.client_listener, args=("Bob", bob_q))
    t1.start()
    t2.start()

    time.sleep(0.5)

    # Alice sends to Bob
    server.send_message("Alice", "Bob", "Hello Bob!")
    time.sleep(0.5)

    # Bob sends to Alice
    server.send_message("Bob", "Alice", "Hey Alice, wassup?")
    time.sleep(0.5)

    # Carol (offline)
    server.send_message("Alice", "Carol", "Are you there?")

    t1.join()
    t2.join()
```

**Output:**
```
✅ User Alice connected.
✅ User Bob connected.
   🚀 Pushed to Bob: Hello Bob!
   📲 Bob received from Alice: Hello Bob!
   🚀 Pushed to Alice: Hey Alice, wassup?
   📲 Alice received from Bob: Hey Alice, wassup?
   💤 User Carol offline. Queued push notification.
```

---

## 🧠 Interview Nuances

### 1. Which Database?
*   **SQL (MySQL)**: Good for small scale, relations. Hard to scale writes for billions of messages.
*   **NoSQL (Cassandra/HBase)**: **Preferred**.
    *   Wide-column store.
    *   Partition Key: `chat_id`.
    *   Clustering Key: `timestamp`.
    *   Efficient range queries (Get last 50 messages).

### 2. How to handle "Last Seen"?
*   Heartbeat mechanism. Client sends "I'm alive" every 5 seconds.
*   Store in **Redis** with TTL = 10s.
*   If user stops sending, Key expires -> User is offline.
*   **Don't** write every heartbeat to the main DB (too much load).

### 3. End-to-End Encryption (E2EE)?
*   Server stores **only encrypted blobs**. It cannot read messages.
*   **Signal Protocol**:
    *   Alice generates public/private key pair.
    *   Bob fetches Alice's public key to encrypt.
    *   Alice uses her private key to decrypt.

---

## ⚡ Flashcards
1.  **WebSocket vs Long Polling?**
    *   WebSocket: Full-duplex, persistent, low overhead.
    *   Long Polling: Client requests, server holds until data available. High header overhead.
2.  **Why Cassandra for Chat?**
    *   Extremely high write throughput. Good for time-series data (Chat logs).
3.  **Fan-out on Read vs Write (Group Chat)?**
    *   **Write (Push)**: Sender pushes to all 100 members. Low read latency. (Better for chat).
    *   **Read (Pull)**: Every member pulls from Sender's inbox. High read latency.
