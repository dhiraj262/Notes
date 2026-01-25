# Day 47: Design Case - Distributed Key-Value Store

## 🎯 Goal
Design a highly available and scalable Key-Value store similar to **Amazon Dynamo** or **Cassandra**.
**Focus**: Partitioning, Replication, and Tunable Consistency.

---

## 🗣️ Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Scalable**: Must handle massive data (PB scale).
3.  **High Availability**: Works even if nodes fail.

### Non-Functional
1.  **Low Latency**: < 10ms for Read/Write.
2.  **Partition Tolerance**: System continues to function during network partitions.
3.  **Tunable Consistency**: Allow users to choose Strong vs Eventual consistency.

---

## 📐 Capacity Estimation
*   **Data**: 100 TB.
*   **QPS**: 100k requests/second.
*   **Nodes**: If 1 node holds 1TB, we need 100 nodes.
*   **Replication**: Factor of 3 -> **300 nodes**.

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: Simple `hash(key) % N` breaks when N changes (reshuffling).
*   **Solution**: **Consistent Hashing**.
    *   Map nodes and keys to a Ring (0 - 2^32).
    *   Key is stored in the first node found clockwise.
    *   **Virtual Nodes**: One physical node maps to multiple points on the ring to balance load.

### 2. Replication
*   **Master-Slave**: Bottleneck on Master.
*   **Leaderless (Dynamo style)**: Any node can accept writes.
*   **Strategy**: Replicate data to the coordinator node + next `N-1` nodes on the ring.

### 3. Consistency: Quorums (N, R, W)
*   **N**: Replicas (e.g., 3).
*   **W**: Write Quorum (e.g., 2). Must write to 2 nodes to succeed.
*   **R**: Read Quorum (e.g., 2). Must read from 2 nodes to succeed.
*   **Strong Consistency**: `R + W > N`.
*   **Eventual Consistency**: `R + W <= N` (Faster, but risk of stale data).

### 4. Conflict Resolution
*   If two users update same key on different nodes at same time.
*   **Last Write Wins (LWW)**: Use timestamp. (Simple, but can lose data).
*   **Vector Clocks**: Track version history `[NodeA:1, NodeB:2]`. (Complex, preserves history).

---

## 🏗️ System Architecture

1.  **Client**: Connects to Load Balancer.
2.  **Coordinator Node**: Any node can act as coordinator. Has partition map.
3.  **Gossip Protocol**: Nodes talk to each other to detect failures ("I see Node A is down").
4.  **Merkle Trees**: Used to compare data between replicas efficiently for repair.
5.  **Hinted Handoff**: If Node A is down, write to Node B with a "hint" to send back to A later.

---

## 💻 Code Simulation: Consistent Hashing

Simulating a **Consistent Hash Ring** with **Virtual Nodes** to map keys to servers.

```python
import hashlib
import bisect

class ConsistentHashing:
    def __init__(self, num_replicas=3):
        self.num_replicas = num_replicas
        self.ring = [] # List of (hash, node_name)
        self.nodes = set()

    def _hash(self, key):
        """Returns a hash integer for the key using MD5"""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node_name):
        """Adds a physical node and its virtual replicas to the ring"""
        print(f"➕ Adding Node: {node_name}")
        self.nodes.add(node_name)
        for i in range(self.num_replicas):
            virtual_node_key = f"{node_name}#{i}"
            h = self._hash(virtual_node_key)
            # Insert into sorted ring
            bisect.insort(self.ring, (h, node_name))

    def remove_node(self, node_name):
        """Removes a physical node and its virtual replicas"""
        print(f"➖ Removing Node: {node_name}")
        self.nodes.remove(node_name)
        # Rebuild ring excluding this node
        self.ring = [x for x in self.ring if x[1] != node_name]

    def get_node(self, key):
        """Finds the node responsible for the key"""
        if not self.ring:
            return None

        h = self._hash(key)

        # Binary search to find the first node >= hash
        # We search for (h, "") which works because tuple comparison checks first element
        idx = bisect.bisect_left(self.ring, (h, ""))

        if idx == len(self.ring):
            # Wrap around to the start
            return self.ring[0][1]
        else:
            return self.ring[idx][1]

if __name__ == "__main__":
    ch = ConsistentHashing(num_replicas=3)

    # 1. Add Servers
    ch.add_node("Server_A")
    ch.add_node("Server_B")
    ch.add_node("Server_C")

    # 2. Map Keys
    keys = ["User_1", "User_2", "User_3", "Order_99", "Payment_X"]
    print("\n--- Initial Mapping ---")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' -> {node}")

    # 3. Add a new Server (Scaling out)
    print("\n--- Scaling Out ---")
    ch.add_node("Server_D")

    print("\n--- New Mapping (Minimal Reshuffling) ---")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' -> {node}")
```

**Output:**
```
➕ Adding Node: Server_A
➕ Adding Node: Server_B
➕ Adding Node: Server_C

--- Initial Mapping ---
Key 'User_1' -> Server_B
Key 'User_2' -> Server_A
Key 'User_3' -> Server_C
Key 'Order_99' -> Server_B
Key 'Payment_X' -> Server_A

--- Scaling Out ---
➕ Adding Node: Server_D

--- New Mapping (Minimal Reshuffling) ---
Key 'User_1' -> Server_B
Key 'User_2' -> Server_A
Key 'User_3' -> Server_D  <-- Changed (Reshuffled)
Key 'Order_99' -> Server_B
Key 'Payment_X' -> Server_A
```
*(Note: Only 'User_3' moved to the new Server D. Others stayed put. This is the power of Consistent Hashing.)*

---

## 🧠 Interview Nuances

### 1. Explain CAP Theorem in this context.
*   Dynamo/Cassandra are **AP** (Available + Partition Tolerant). They sacrifice Strong Consistency for Availability.
*   You might get stale data (Eventual Consistency).

### 2. What is Sloppy Quorum?
*   If Node A is down, the system writes to Node D (which isn't in the preference list) just to satisfy `W=2`.
*   This ensures high availability but lowers consistency guarantees.

### 3. How does repair happen?
*   **Read Repair**: When reading, if Node A has v1 and Node B has v2, the system returns v2 and updates Node A in the background.
*   **Anti-Entropy**: Background process using Merkle Trees to compare data across nodes and sync huge datasets efficiently.

---

## ⚡ Flashcards
1.  **What is the benefit of Virtual Nodes?**
    *   Better load balancing. If Server A is powerful, give it more virtual nodes. If Server B fails, its load is distributed evenly to A and C, not just C.
2.  **What is Gossip Protocol?**
    *   Peer-to-peer communication where nodes randomly share state info. "I heard A is alive". Efficient way to manage cluster state without a central Master.
3.  **LSM Tree vs B-Tree for KV Store?**
    *   **LSM Tree (Cassandra)**: Fast Writes (Append only). Slower Reads (Check memtable -> SS Tables).
    *   **B-Tree (DynamoDB/MySQL)**: Balanced Read/Write.
