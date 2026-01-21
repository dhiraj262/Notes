# Day 47: Design Case - Distributed Key-Value Store

## 🎯 Goal
Design a highly available and scalable Key-Value store (like Amazon DynamoDB or Apache Cassandra).
**Focus**: Partitioning, Replication, and Consistency trade-offs (CAP Theorem).

---

## 🗣️ Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Configurable Consistency**: Allow users to choose Strong vs Eventual consistency.

### Non-Functional
1.  **High Availability**: System must work even if nodes fail (AP > CP usually).
2.  **Scalability**: Linear scale with more nodes.
3.  **Fault Tolerance**: No single point of failure.

---

## 📐 Capacity Estimation
*   **Scale**: 100TB Data.
*   **Replication Factor**: 3. Total Storage = 300TB.
*   **Nodes**: If 1 node holds 1TB -> 300 Nodes.

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: `hash(k) % N`. If N changes (add node), most keys move.
*   **Solution**: **Consistent Hashing** (Ring).
    *   Keys and Nodes map to a ring (0 to 2^64).
    *   Node stores keys strictly clockwise from its position.
    *   Virtual Nodes: One physical node maps to multiple points on ring (Balances load).

### 2. Data Replication
*   **Strategy**: Replicate key to `N` successive nodes in the ring.
*   **Leaderless**: Any node can accept a write (Dynamo style). No single master bottleneck.

### 3. Consistency: Quorums
*   **N**: Replicas (e.g., 3).
*   **W**: Write Quorum (Ack needed from W nodes).
*   **R**: Read Quorum (Data from R nodes).
*   **Formula**: If `W + R > N`, we have Strong Consistency (Overlap guarantees reading latest write).
    *   Example: N=3, W=2, R=2.

---

## 🏗️ System Architecture

1.  **Client** sends `put(k, v)`.
2.  **Coordinator Node** (Any node acting as proxy):
    *   Hashes `k` to find preference list (Nodes A, B, C).
    *   Sends Write to A, B, C.
    *   Waits for `W` acks.
    *   Returns Success.
3.  **Failure Handling**:
    *   **Hinted Handoff**: If Node A is down, write to Node D (with a note "Give to A later").
    *   **Read Repair**: On Read, if replicas differ, return latest version and update stale ones.
    *   **Anti-Entropy**: Background process using **Merkle Trees** to compare data and sync.

---

## 💻 Code Simulation: Consistent Hashing

```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas # Virtual nodes
        self.ring = []
        self.node_map = {} # Hash -> Node Name

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            bisect.insort(self.ring, key)
            self.node_map[key] = node

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring.remove(key)
            del self.node_map[key]

    def get_node(self, key):
        if not self.ring:
            return None
        h = self._hash(key)
        # Find first hash on ring >= h
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0 # Wrap around
        return self.node_map[self.ring[idx]]

if __name__ == "__main__":
    ch = ConsistentHash(nodes=["NodeA", "NodeB", "NodeC"])

    keys = ["user_1", "user_2", "order_99", "data_x"]
    for k in keys:
        print(f"Key '{k}' maps to -> {ch.get_node(k)}")

    print("\n--- Adding NodeD ---")
    ch.add_node("NodeD")
    for k in keys:
        print(f"Key '{k}' maps to -> {ch.get_node(k)}")
```

---

## 🧠 Interview Nuances

### 1. Conflict Resolution?
*   In Leaderless replication, two clients can write to Key X at the same time.
*   **Last Write Wins (LWW)**: Based on timestamp (Clock skew issues).
*   **Vector Clocks**: Keep version history `[NodeA:1, NodeB:2]`. Detects causal history vs concurrent conflicts. Client must resolve.

### 2. Gossip Protocol?
*   How do nodes know who is alive?
*   Every second, each node picks a random node and exchanges state info ("I am alive", "Node A is dead"). Info spreads like a virus.

---

## ⚡ Flashcards
1.  **What is a Merkle Tree?**
    *   A hash tree where leaves are data hashes and parents are hashes of children. Allows efficient comparison of huge data sets to find differences.
2.  **What is Tunable Consistency?**
    *   The ability to change W and R per request. (e.g., Critical data: W=3, R=1. Fast data: W=1, R=1).
3.  **Hinted Handoff?**
    *   Writing to a temporary node if the target is down, ensuring availability (Write always succeeds).
