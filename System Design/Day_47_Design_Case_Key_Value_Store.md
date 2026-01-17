# Day 47: Design Case - Distributed Key-Value Store (Dynamo/Cassandra)

## 🎯 Goal
Design a highly available and scalable Key-Value store similar to Amazon Dynamo or Apache Cassandra.
**Focus**: Partitioning, Replication, Consistency, and Failure Handling.

---

## 🗣️ Requirements

### Functional
1.  **put(key, value)**: Store object.
2.  **get(key)**: Retrieve object.
3.  **Configurable Consistency**: Allow users to choose Strong vs Eventual Consistency.

### Non-Functional
1.  **High Availability**: System must work even if nodes fail.
2.  **Scalability**: Linear scale with more nodes.
3.  **Low Latency**: Key access should be fast.

---

## 📐 Capacity Estimation
*   **Data**: 100 TB.
*   **Replication Factor**: 3 -> 300 TB total storage.
*   **QPS**: 100k writes/sec, 500k reads/sec.
*   **Node Capacity**: If 1 node holds 1TB, we need ~300 nodes.

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: `hash(key) % N` breaks when N changes (all keys move).
*   **Solution**: **Consistent Hashing**.
    *   Map nodes to a Ring (0 to 2^128 - 1).
    *   Map keys to the Ring.
    *   Key K is stored on the first node found clockwise.
    *   **Virtual Nodes**: Each physical node maps to multiple points on the ring to ensure even load distribution.

### 2. Data Replication
*   Replicate Key K to the coordinator node + next N-1 nodes on the ring.
*   **Preference List**: List of nodes responsible for a key.

### 3. Consistency: Quorum Consensus
*   **N**: Number of replicas (e.g., 3).
*   **W**: Write Quorum (min nodes to acknowledge write).
*   **R**: Read Quorum (min nodes to acknowledge read).
*   **Strong Consistency**: If `W + R > N`.
    *   Example: N=3, W=2, R=2. (2+2 > 3).
*   **Eventual Consistency**: If `W + R <= N`. Faster, but risk of stale data.

---

## 🏗️ System Architecture

1.  **Client**: Uses a library to find the right node (Coordinator).
2.  **Coordinator Node**: The node handling the request.
    *   **Write**: Sends data to N replicas. Waits for W acks.
    *   **Read**: Asks N replicas. Waits for R responses. Returns latest version (Vector Clock).
3.  **Failure Handling**:
    *   **Gossip Protocol**: Nodes talk to each other to detect failures.
    *   **Sloppy Quorum**: If Node A is down, write to Node D temporarily (Hinted Handoff).
    *   **Anti-Entropy**: Use **Merkle Trees** to compare data between nodes and sync differences efficiently.

---

## 💻 Code Simulation: Consistent Hashing

A Python implementation of Consistent Hashing with Virtual Nodes.

```python
import hashlib
import bisect

class ConsistentHashing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas # Virtual nodes per physical node
        self.ring = []           # Sorted list of hash values
        self.node_map = {}       # Hash -> Node Name

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # MD5 returns 128-bit hash
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = f"{node}:{i}"
            h = self._hash(key)
            self.ring.append(h)
            self.node_map[h] = node
        self.ring.sort()
        print(f"Added node {node}. Ring size: {len(self.ring)}")

    def remove_node(self, node):
        for i in range(self.replicas):
            key = f"{node}:{i}"
            h = self._hash(key)
            if h in self.ring:
                self.ring.remove(h)
                del self.node_map[h]
        print(f"Removed node {node}. Ring size: {len(self.ring)}")

    def get_node(self, key):
        if not self.ring:
            return None
        h = self._hash(key)
        # Binary search for the first hash >= h
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0 # Wrap around
        node_hash = self.ring[idx]
        return self.node_map[node_hash]

if __name__ == "__main__":
    ch = ConsistentHashing(["NodeA", "NodeB", "NodeC"])

    keys = ["user_1", "user_2", "order_101", "payment_500"]

    print("\n--- Distribution ---")
    for k in keys:
        print(f"Key '{k}' maps to -> {ch.get_node(k)}")

    print("\n--- Adding NodeD ---")
    ch.add_node("NodeD")

    print("\n--- New Distribution ---")
    for k in keys:
        print(f"Key '{k}' maps to -> {ch.get_node(k)}")
```

**Output:**
```
Added node NodeA. Ring size: 3
Added node NodeB. Ring size: 6
Added node NodeC. Ring size: 9

--- Distribution ---
Key 'user_1' maps to -> NodeB
Key 'user_2' maps to -> NodeB
Key 'order_101' maps to -> NodeA
Key 'payment_500' maps to -> NodeB

--- Adding NodeD ---
Added node NodeD. Ring size: 12

--- New Distribution ---
Key 'user_1' maps to -> NodeB
Key 'user_2' maps to -> NodeB
Key 'order_101' maps to -> NodeA
Key 'payment_500' maps to -> NodeB
```

---

## 🧠 Interview Nuances

### 1. Vector Clocks?
*   Used to resolve conflicts.
*   If Node A and Node B update Key X at the same time, we have siblings.
*   Client must reconcile siblings (e.g., merge shopping carts).

### 2. How to detect failures?
*   **Phi Accrual Failure Detector**: Instead of binary (Up/Down), calculate probability of failure based on heartbeat timing.

### 3. Read Repair vs Anti-Entropy?
*   **Read Repair**: Fix data when client reads stale data. (Lazy).
*   **Anti-Entropy**: Background process (Merkle Trees) to sync data. (Proactive).

---

## ⚡ Flashcards
1.  **What is Tunable Consistency?**
    *   The ability to choose W and R to balance between Latency (low W/R) and Consistency (high W/R).
2.  **Why use Virtual Nodes in Consistent Hashing?**
    *   To improve load balancing. If one node is more powerful, give it more virtual nodes. Also helps distribute data evenly when a node is added/removed.
3.  **What is a Merkle Tree?**
    *   A hash tree where leaves are data hashes and parents are hashes of children. Used to quickly compare large datasets between nodes.
