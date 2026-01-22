# Day 47: Design Case - Distributed Key-Value Store (Dynamo/Cassandra)

## 🎯 Goal
Design a highly available, scalable Key-Value store (like Amazon Dynamo, Cassandra, or Riak).

---

## 🗣️ Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Scalability**: Must handle massive data growth (add nodes without downtime).
3.  **Configurable Consistency**: Allow users to choose Strong vs Eventual consistency.

### Non-Functional
1.  **High Availability**: System should continue to operate even if nodes fail (AP over CP).
2.  **Fault Tolerance**: Replicate data across nodes.
3.  **Low Latency**: Read/Write < 10ms.

---

## 📐 Capacity Estimation
*   **Data**: 1 PB.
*   **Replication Factor**: 3 (Total 3 PB).
*   **Throughput**: 1 Million QPS.
*   **Nodes**: If each node handles 10k QPS, we need ~100 nodes.

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: `hash(key) % N` breaks when N changes (re-shuffling all data).
*   **Solution**: **Consistent Hashing** (Hash Ring).
    *   Map both Nodes and Keys to a circle (0 - 2^32).
    *   Key maps to the first Node found clockwise.
    *   **Virtual Nodes**: Each physical server appears multiple times on the ring to balance load.

### 2. Data Replication
*   Data is replicated to the coordinator node + next 2 nodes on the ring.
*   **Preference List**: List of nodes responsible for a key.

### 3. Consistency: Quorum Consensus (N, W, R)
*   **N** = Number of Replicas (e.g., 3).
*   **W** = Write Quorum (Ack needed from W nodes).
*   **R** = Read Quorum (Response needed from R nodes).
*   **Strong Consistency**: W + R > N. (e.g., W=2, R=2, N=3).
*   **Eventual Consistency**: W + R <= N. (Fast, but risk of stale data).

### 4. Conflict Resolution
*   If two writes happen simultaneously on different replicas (Split Brain), we get siblings.
*   **Vector Clocks**: Attach a version counter `[NodeA: 1, NodeB: 2]` to data.
*   **Last Write Wins (LWW)**: Use timestamp (simple, but can lose data).

---

## 🏗️ System Architecture

1.  **Client** requests `put(key, val)`.
2.  **Load Balancer** routes to any Node (Coordinator).
3.  **Coordinator**:
    *   Hashes key to find the "Home" node.
    *   Forwards data to Home + (N-1) Replicas in parallel.
    *   Waits for **W** acks.
    *   Returns Success.
4.  **Anti-Entropy (Gossip Protocol)**:
    *   Nodes periodically exchange information to detect failures.
    *   **Merkle Trees**: Compare hash trees of data ranges to sync replicas efficiently.

---

## 💻 Code Simulation: Consistent Hashing Ring

Simulates the distribution of keys and minimal movement when adding a node.

```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas  # Virtual nodes per physical node
        self.ring = {}            # Hash -> Node Name
        self.sorted_keys = []     # Sorted Hashes

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # MD5 provides good distribution
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)
        print(f"✅ Added Node: {node}")

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            if key in self.ring:
                del self.ring[key]
                self.sorted_keys.remove(key)
        print(f"❌ Removed Node: {node}")

    def get_node(self, key):
        if not self.ring:
            return None

        hash_val = self._hash(key)
        # Find the first key on ring >= hash_val
        idx = bisect.bisect_left(self.sorted_keys, hash_val)

        if idx == len(self.sorted_keys):
            idx = 0 # Wrap around (Circle)

        return self.ring[self.sorted_keys[idx]]

# Simulation usage
if __name__ == "__main__":
    ch = ConsistentHash(nodes=["Server_A", "Server_B", "Server_C"], replicas=3)

    keys = ["user_101", "user_204", "order_55", "payment_99"]

    print("\n📍 Initial Mapping:")
    for k in keys:
        print(f"   Key '{k}' -> {ch.get_node(k)}")

    print("\n⚙️ Scaling Out (Adding Server_D)...")
    ch.add_node("Server_D")

    print("\n📍 New Mapping:")
    for k in keys:
        print(f"   Key '{k}' -> {ch.get_node(k)}")
```

---

## 🧠 Interview Nuances

### 1. How to detect node failures?
*   **Gossip Protocol**: Nodes talk to random peers periodically ("I'm alive"). If Node A stops gossiping, others mark it as dead.

### 2. What are Hinted Handoffs?
*   If Node A is down, Coordinator writes to Node B (temporary).
*   Node B holds a "hint" that "This belongs to A".
*   When A comes back, B hands the data back.

### 3. Sloppy Quorum?
*   If the "Home" nodes are down, write to *any* healthy nodes to satisfy W. Allows high write availability at the cost of consistency.

---

## ⚡ Flashcards
1.  **What is a Virtual Node?**
    *   A technique in consistent hashing where one physical server is mapped to multiple points on the ring to improve load balance and reduce "hot spots".
2.  **CAP Theorem trade-off for Dynamo?**
    *   Dynamo chooses **AP** (Availability + Partition Tolerance), sacrificing Strong Consistency for Eventual Consistency.
3.  **What is a Merkle Tree?**
    *   A tree of hashes used to efficiently verify data integrity and sync differences between replicas without sending the entire dataset.
