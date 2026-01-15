# Day 47: Design a Key-Value Store (Dynamo/Cassandra)

## 🎯 Goal
Design a highly available, scalable Key-Value store like Amazon Dynamo, Apache Cassandra, or Riak.
**Focus**: Partitioning (Consistent Hashing), Replication, and Tunable Consistency (Quorums).

---

## 🗣️ Requirements

### Functional
1.  **put(key, value)**: Store object.
2.  **get(key)**: Retrieve object.
3.  **Configurable Consistency**: Allow trading consistency for availability (AP system).

### Non-Functional
1.  **High Availability**: System should always accept writes (even during network partitions).
2.  **Scalability**: Linear scaling (Add nodes = More capacity).
3.  **Fault Tolerance**: Handle node failures without data loss.

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: `hash(key) % N`. If `N` changes, almost ALL keys move.
*   **Solution**: **Consistent Hashing Ring**.
    *   Map nodes and keys to a circle (0-2^32).
    *   Key maps to the next clockwise node.
    *   Adding a node only affects its immediate neighbor.
    *   **Virtual Nodes**: Each physical node appears multiple times on the ring to balance load.

### 2. Replication: Preference List
*   Data is replicated to `N` nodes (usually 3).
*   Coordinator node copies data to the next `N-1` nodes on the ring.

### 3. Consistency: Quorum Consensus
*   **W (Write Quorum)**: Min nodes that must acknowledge write.
*   **R (Read Quorum)**: Min nodes that must respond to read.
*   **Formula**: `W + R > N` (Strong Consistency).
*   **Configurable**:
    *   `W=1` (Fast writes, risk data loss).
    *   `W=All` (Slow writes, strong durability).

---

## 🏗️ System Architecture

1.  **Coordinator Node**: Any node can receive a request. It acts as a coordinator for that key.
2.  **Gossip Protocol**: Nodes periodically exchange state ("I am alive", "Node B is down"). Decentralized failure detection.
3.  **Merkle Trees**: Used to compare data between replicas efficiently. If hashes differ, sync only the difference.
4.  **SSTables & WAL**:
    *   Writes go to **Commit Log** (WAL) on disk (Durability).
    *   Then to **MemTable** (RAM).
    *   Flushed to **SSTable** (Disk) when full.

---

## 💻 Code Simulation: Consistent Hashing

Simulating the ring and node lookups.

```python
import hashlib

class ConsistentHashing:
    def __init__(self, nodes, replicas=3):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        for node in nodes:
            self.add_node(node)

    def _hash(self, key):
        # Using MD5 for deterministic hashing
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        self.sorted_keys.sort()
        print(f"✅ Added Node: {node} (Virtual nodes: {self.replicas})")

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)
        print(f"❌ Removed Node: {node}")

    def get_node(self, item):
        if not self.ring:
            return None
        key = self._hash(item)
        # Binary Search could be used here for O(logN)
        for k in self.sorted_keys:
            if k >= key:
                return self.ring[k]
        # Wrap around to the first node
        return self.ring[self.sorted_keys[0]]

if __name__ == "__main__":
    cluster = ConsistentHashing(["Node_A", "Node_B", "Node_C"], replicas=2)

    items = ["User_1", "User_2", "User_3", "User_4", "User_5"]

    print("\n📍 Initial Distribution:")
    for item in items:
        print(f"   {item} -> {cluster.get_node(item)}")

    # Add a new node
    print("\n🔄 Scaling Up (Adding Node_D)...")
    cluster.add_node("Node_D")

    print("\n📍 New Distribution:")
    for item in items:
        print(f"   {item} -> {cluster.get_node(item)}")
```

**Output:**
```
✅ Added Node: Node_A (Virtual nodes: 2)
...
📍 Initial Distribution:
   User_1 -> Node_A
   User_5 -> Node_B
...
🔄 Scaling Up (Adding Node_D)...
📍 New Distribution:
   User_5 -> Node_D  (Only User_5 moved!)
```

---

## 🧠 Interview Nuances

### 1. How to handle temporary failures? (Hinted Handoff)
*   If Node A is down, Coordinator writes to Node B (hinted).
*   When Node A returns, Node B hands back the data.
*   Ensures "Always Writable".

### 2. Conflict Resolution?
*   **Last Write Wins (LWW)**: Based on timestamp (Clock skew issues).
*   **Vector Clocks**: Capture causality. `[A:1, B:2]`. If concurrent, return both versions to client for resolution.

### 3. Anti-Entropy?
*   How to fix data rot? Use **Read Repair** (fix on read) and **Anti-Entropy** (background Merkle Tree sync).

---

## ⚡ Flashcards
1.  **What is a Virtual Node?**
    *   A technique to distribute a physical node across multiple points on the hash ring to ensure even load distribution.
2.  **What is Tunable Consistency?**
    *   The ability to choose `W` and `R` parameters. `W=1` for speed, `W=Quorum` for consistency.
3.  **What is a Bloom Filter in Cassandra?**
    *   A probabilistic data structure used to quickly check if an SSTable contains a key, saving disk I/O.
