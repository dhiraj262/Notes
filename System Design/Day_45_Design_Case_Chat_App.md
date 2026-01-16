# Day 45: Design a Chat App (WhatsApp/Messenger)

## 🎯 Goal
Design a massively scalable instant messaging application like WhatsApp, Facebook Messenger, or WeChat that supports **1-on-1 chat**, **Group chat**, and **Online Status** indicators.

## 📋 Requirements

### Functional
1.  **1-on-1 Chat**: Low latency delivery.
2.  **Group Chat**: Support for groups (e.g., up to 256 members).
3.  **Online Status**: Show if a user is Online/Offline/Last Seen.
4.  **Message Status**: Sent, Delivered, Read receipts.
5.  **Media Support**: Images/Video (Out of scope for core logic, but mention Blob storage).
6.  **Persistent History**: Messages are stored and accessible across devices.

### Non-Functional
1.  **Low Latency**: Real-time experience is critical.
2.  **High Availability**: No downtime.
3.  **High Consistency**: Messages must be ordered and not lost.
4.  **Scale**: 2 Billion users, 100 Billion messages/day.

## 🔢 Capacity Estimation (Back-of-the-Envelope)

*   **Traffic**:
    *   100 Billion messages / day.
    *   Daily Active Users (DAU): 1 Billion.
    *   QPS (Average) = $100 \times 10^9 / 86400 \approx 1.2M$ msg/sec.
    *   Peak QPS = $1.2M \times 5 \approx 6M$ msg/sec.
*   **Storage**:
    *   Avg message size = 100 bytes (text).
    *   Daily Storage = $100B \times 100B = 10TB$ / day.
    *   5 Years = $10TB \times 365 \times 5 \approx 18PB$.
*   **Bandwidth**:
    *   Ingress: $10TB / 86400 \approx 115 MB/s$ (seems low for text, but media drives this up significantly).

## 🏗️ Architecture Design

### 1. Connection Handling (WebSockets)
Unlike standard HTTP, chat requires persistent connections for bi-directional communication.
*   **Protocol**: **WebSocket** is preferred over HTTP polling for real-time latency and reduced overhead.
*   **Chat Servers**: Stateful servers holding open WebSocket connections for active users.

### 2. Service Discovery
How do we know which Chat Server holds Alice's connection?
*   **Zookeeper / Redis**: Maintains a mapping of `User_ID -> Gateway_Server_IP`.
*   When Bob sends a message to Alice, the system looks up Alice's server and routes the message there.

### 3. Database Choice
We need **extremely high write throughput** and range queries (fetch history).
*   **RDBMS (MySQL/Postgres)**: Hard to scale to 100B writes/day without massive sharding. Good for user profiles (low volume).
*   **NoSQL (Wide Column)**: **HBase** or **Cassandra**.
    *   *Discord uses Cassandra (and later ScyllaDB).*
    *   *Facebook Messenger uses HBase.*
    *   **Why?** Efficient localized writes, great for time-series data (chat history).
    *   **Row Key**: `Chat_ID + Timestamp` (Cluster by chat, sort by time).

### 4. Message Flow
1.  **Alice** sends msg to LB.
2.  LB routes to **Chat Server 1** (where Alice is connected).
3.  Server 1 writes msg to **NoSQL DB** (for history/backup).
4.  Server 1 queries **Service Discovery** to find Bob's location.
5.  **Scenario A (Bob Online)**:
    *   Bob is on **Chat Server 2**.
    *   Server 1 forwards msg to Server 2 (via RPC or internal queue).
    *   Server 2 pushes to Bob via WebSocket.
6.  **Scenario B (Bob Offline)**:
    *   Server 1 pushes msg to **Push Notification Service** (FCM/APNS).

### 5. Group Chat Fan-out
*   **Small Group (<200)**: Server iterates through member list and pushes individually.
*   **Large Group/Channel (>5000)**: Do not push immediately. Client uses "Pull" mechanism or system uses a **Message Queue** (Kafka) topic per group to decouple processing.

## 🐍 Code Simulation
A Python simulation of the core routing logic.

```python
import uuid
import time
from collections import defaultdict, deque
from typing import Dict, List, Optional

class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.is_online = False
        self.connection_id = None  # Mocking a WebSocket connection ID

class Message:
    def __init__(self, sender_id, receiver_id, content, group_id=None):
        self.message_id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.group_id = group_id
        self.content = content
        self.timestamp = time.time()
        self.status = "SENT"  # SENT, DELIVERED, READ

class ChatService:
    def __init__(self):
        self.users: Dict[str, User] = {}
        # Service Discovery: Maps UserID -> ServerID (simplified here as just presence)
        self.user_connections: Dict[str, str] = {}
        # DB: Chat History
        self.message_store: Dict[str, List[Message]] = defaultdict(list)
        # Offline Queue (simulating external queue like RabbitMQ/Kafka for offline users)
        self.offline_queue: Dict[str, List[Message]] = defaultdict(list)

    def register_user(self, user_id, name):
        self.users[user_id] = User(user_id, name)
        print(f"[System] Registered user: {name} ({user_id})")

    def connect_user(self, user_id):
        if user_id in self.users:
            self.users[user_id].is_online = True
            print(f"[Network] User {self.users[user_id].name} connected.")
            # Deliver offline messages
            if user_id in self.offline_queue:
                count = len(self.offline_queue[user_id])
                print(f"[System] Delivering {count} offline messages to {self.users[user_id].name}")
                for msg in self.offline_queue[user_id]:
                    msg.status = "DELIVERED"
                    self.message_store[self._get_chat_key(msg.sender_id, user_id)].append(msg)
                del self.offline_queue[user_id]

    def disconnect_user(self, user_id):
        if user_id in self.users:
            self.users[user_id].is_online = False
            print(f"[Network] User {self.users[user_id].name} disconnected.")

    def _get_chat_key(self, u1, u2):
        # Unique key for 1-on-1 chat regardless of sender/receiver order
        return tuple(sorted((u1, u2)))

    def send_private_message(self, sender_id, receiver_id, content):
        msg = Message(sender_id, receiver_id, content)

        # 1. Persist Message (Write-Ahead Log / DB)
        chat_key = self._get_chat_key(sender_id, receiver_id)
        # In reality, we write to Cassandra here.

        receiver = self.users.get(receiver_id)
        if not receiver:
            print(f"[Error] Receiver {receiver_id} not found.")
            return

        print(f"[Message] '{content}' from {self.users[sender_id].name} to {receiver.name}")

        if receiver.is_online:
            # 2. Push via WebSocket (Hot Path)
            msg.status = "DELIVERED"
            self.message_store[chat_key].append(msg)
            print(f"   -> [Push] Delivered to {receiver.name} instantly.")
        else:
            # 3. Store in Offline Queue (Cold Path)
            print(f"   -> [Store] {receiver.name} is offline. Queued.")
            self.offline_queue[receiver_id].append(msg)

# --- Driver Code ---
if __name__ == "__main__":
    system = ChatService()
    system.register_user("u1", "Alice")
    system.register_user("u2", "Bob")

    # Alice sends msg to Bob (Offline)
    system.connect_user("u1")
    system.send_private_message("u1", "u2", "Hello Bob, are you there?")

    # Bob comes online
    print("\n--- Bob comes online ---")
    system.connect_user("u2")

    # Real-time chat
    system.send_private_message("u2", "u1", "Hey Alice, just got online!")
```

## 🧠 Interview Nuances

### "The Trap": Storing messages in MySQL
*   **Problem**: A standard SQL table with `(id, sender, receiver, content)` will degrade rapidly as rows hit billions. Index updates become slow.
*   **Solution**: Use a Column-oriented NoSQL DB (Cassandra/HBase). The access pattern is strictly "Get latest N messages for Chat ID X". Partition by `ChatID`, Cluster key by `Timestamp`.

### "The Kill Shot": Sequence Numbers in Distributed Systems
*   **Challenge**: How do you ensure messages appear in order if they are processed by different servers?
*   **Solution**: You cannot rely on server timestamps (clock skew). Use a **Sequence Generator** (like Snowflake ID or a local counter per chat stored in Redis) to enforce strict ordering within a specific chat session.

### "Production Realities"
*   **Thundering Herd**: When a celebrity sends a message in a massive group, millions of users might try to fetch it. Use a "Push ID, Pull Content" strategy for media, or batch multicast.
*   **Last Seen**: Do not update the DB on every heartbeat. Update Redis every heartbeat, and flush to DB only on session end or every 5 minutes.

## ⚡ Flashcards
*   **Protocol for Real-time?** -> WebSockets (Bi-directional, persistent).
*   **DB for Chat History?** -> Cassandra/HBase (High write throughput, time-series).
*   **Group Chat Fan-out?** -> Loop for small groups; Kafka Topics/Pub-Sub for large groups.
*   **Service Discovery?** -> Zookeeper/Redis to map UserID -> WebSocket Server IP.
