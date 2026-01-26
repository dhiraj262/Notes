# Day 47: Design a Key-Value Store

## 🎯 Goal
Design a highly available and scalable Key-Value Store (like Amazon Dynamo, Cassandra, or Riak).
**Focus**: Partitioning (Consistent Hashing), Replication, and Tunable Consistency (Quorum).

---

## 🗣️ Requirements

### Functional
1.  **put(key, value)**: Store a value associated with a key.
2.  **get(key)**: Retrieve the value associated with a key.
3.  **Configurable Consistency**: Allow clients to choose strong or eventual consistency.

### Non-Functional
1.  **High Availability**: System should continue to work even if nodes fail.
2.  **Scalability**: Linear scalability by adding more nodes.
3.  **Fault Tolerance**: No single point of failure.

---

## 📐 Capacity Estimation
*   **Storage**: 100 TB of data.
*   **Throughput**: 10 Million QPS.
*   **Latency**: Low latency for get/put (< 10ms).

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: Simple `hash(key) % N` breaks when `N` changes (nodes added/removed). Data movement is huge.
*   **Solution**: **Consistent Hashing** (Ring).
    *   Map nodes and keys to a ring (0 to 2^64-1).
    *   Key is stored in the first node found moving clockwise.
    *   **Virtual Nodes**: Each physical node maps to multiple points on the ring to balance load.

### 2. Data Replication
*   To ensure availability, replicate data to `N` nodes (usually 3).
*   **Strategy**: Store key on the coordinator node and the next N-1 nodes on the ring.

### 3. Consistency: Quorum Consensus
*   **N**: Number of replicas (e.g., 3).
*   **W**: Write Quorum (nodes that must acknowledge write).
*   **R**: Read Quorum (nodes that must respond to read).
*   **Formula**: If `R + W > N`, we have Strong Consistency.
    *   Example: N=3, W=2, R=2. (2+2 > 3). Guarantee latest data.
    *   For High Availability: W=1 (Fast writes), but risk of stale reads.

---

## 🏗️ System Architecture

1.  **Client**: Sends `put("user:1", "Alice")`.
2.  **Load Balancer**: Routes to any node in the cluster.
3.  **Coordinator Node**:
    *   Hashes the key: `hash("user:1")`.
    *   Finds the "Preference List" (top N nodes for this key).
    *   Sends Write request to all N nodes.
    *   Waits for `W` acknowledgments.
    *   Returns Success to client.
4.  **Anti-Entropy (Gossip Protocol)**:
    *   Nodes periodically exchange state to detect failures and sync data (Merkle Trees).

---

## 💻 Code Simulation: Consistent Hashing

Simulating the ring structure and finding the node for a key.

```python
import hashlib
import bisect

class ConsistentHashing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = {}  # Map: Hash -> Node Name
        self.sorted_keys = [] # Sorted Hashes

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # MD5 hash returning a large integer
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)
        print(f"✅ Added {node} with {self.replicas} virtual nodes.")

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)
        print(f"❌ Removed {node}.")

    def get_node(self, key):
        if not self.ring:
            return None

        hash_val = self._hash(key)
        # Find the first key on ring >= hash_val
        idx = bisect.bisect(self.sorted_keys, hash_val)

        # Wrap around to 0 if at end
        if idx == len(self.sorted_keys):
            idx = 0

        target_hash = self.sorted_keys[idx]
        return self.ring[target_hash]

if __name__ == "__main__":
    ch = ConsistentHashing(["Node_A", "Node_B", "Node_C"])

    # Distribute Keys
    keys = ["user:1", "user:2", "order:55", "image:png"]
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' maps to -> {node}")

    # Remove a node
    ch.remove_node("Node_B")

    # Check redistribution
    print("\n--- After removing Node_B ---")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' maps to -> {node}")
```

**Output:**
```
✅ Added Node_A with 3 virtual nodes.
✅ Added Node_B with 3 virtual nodes.
✅ Added Node_C with 3 virtual nodes.
Key 'user:1' maps to -> Node_C
Key 'user:2' maps to -> Node_A
Key 'order:55' maps to -> Node_B
Key 'image:png' maps to -> Node_A
❌ Removed Node_B.

--- After removing Node_B ---
Key 'user:1' maps to -> Node_C
Key 'user:2' maps to -> Node_A
Key 'order:55' maps to -> Node_C  <-- Remapped from B to C
Key 'image:png' maps to -> Node_A
```

---

## 🧠 Interview Nuances

### 1. Vector Clocks?
*   Used to detect conflicts in Leaderless replication (like Dynamo).
*   If two writes happen to the same key on different nodes (network partition), they have different vector clocks.
*   Client must reconcile the conflict.

### 2. Hinted Handoff?
*   If the target node A is down, write to a temporary node X (with a "hint" that it belongs to A).
*   When A comes back, X sends the data to A.
*   Ensures "Sloppy Quorum" (High Availability).

### 3. Merkle Trees?
*   Efficient way to compare data between nodes.
*   Instead of sending the whole DB to check sync, compare Root Hash. If different, go down the tree to find the specific bucket that differs.

---

## ⚡ Flashcards
1.  **What is the CAP Theorem trade-off for Dynamo?**
    *   Dynamo chooses AP (Availability + Partition Tolerance) over Consistency. It offers Eventual Consistency.
2.  **Why use Virtual Nodes?**
    *   To distribute data more evenly across the ring and prevent "hotspots" if one node is slightly more powerful or luckier with hashing.
3.  **What is 'Gossip Protocol'?**
    *   A peer-to-peer communication protocol where nodes randomly share state information with neighbors, eventually propagating info to the whole cluster.
