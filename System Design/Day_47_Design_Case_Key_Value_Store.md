# Day 47: Design a Key-Value Store (Dynamo/Cassandra)

## 🎯 Goal
Design a highly available, scalable Key-Value store similar to Amazon Dynamo or Apache Cassandra.
**Focus**: Partitioning, Replication, and Tunable Consistency.

---

## 🗣️ Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Scalability**: Must handle massive data growth (Petabytes).
3.  **Configurable Consistency**: Allow users to choose Strong vs Eventual Consistency.

### Non-Functional
1.  **High Availability**: System should work even if nodes fail. "Always Writeable".
2.  **Low Latency**: < 10ms for read/write.
3.  **No Single Point of Failure**: Decentralized (P2P).

---

## 📐 Capacity Estimation
*   **Data Size**: 10 PB.
*   **Nodes**: If one node holds 10TB, we need 1,000 nodes.
*   **QPS**: 10 Million QPS.
*   *Conclusion*: We need sophisticated partitioning (Sharding).

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: `hash(key) % N` breaks when N changes (adding/removing nodes).
*   **Solution**: **Consistent Hashing** (Ring).
    *   Keys are mapped to a ring. Nodes are points on the ring.
    *   Key K maps to the first Node found moving clockwise.
    *   **Virtual Nodes**: Each physical node appears at multiple points on the ring to balance load.

### 2. Replication (N=3)
*   Data is replicated to N nodes (Preference List).
*   Typically, the "Coordinator" node writes to itself and the next N-1 nodes on the ring.

### 3. Consistency: Quorum Consensus (R + W > N)
*   **N**: Number of replicas (e.g., 3).
*   **W**: Write Quorum (How many must acknowledge write).
*   **R**: Read Quorum (How many must respond to read).
*   **Strong Consistency**: If W + R > N (e.g., 2 + 2 > 3). Overlap ensures we read latest data.
*   **Eventual Consistency**: If W=1 (Fast write), we might read old data.

### 4. Conflict Resolution
*   If two nodes accept writes for the same key (Net Split), we get conflicts.
*   **Vector Clocks**: Attach `[NodeA:1, NodeB:2]` version to data.
*   **Last Write Wins (LWW)**: Use timestamp. Simpler, but data loss possible.

---

## 🏗️ System Architecture

1.  **Client**: Connects to any node (Coordinator).
2.  **Coordinator Node**:
    *   Hashes key to find target nodes.
    *   For **Write**: Sends data to W replicas. Uses **Sloppy Quorum** (write to hinted handoff if target down).
    *   For **Read**: Asks R replicas. If versions differ, performs **Read Repair**.
3.  **Gossip Protocol**: Nodes talk to each other every second to detect failures (Heartbeat).
4.  **Merkle Trees**: Used to compare data between nodes efficiently during anti-entropy (sync).

---

## 💻 Code Simulation: Consistent Hashing

Simulating how keys are mapped to nodes using a Hash Ring.

```python
import hashlib

class ConsistentHashing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = {} # Hash -> Node
        self.sorted_keys = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        """Returns a hash integer."""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        """Add a node (and its virtual replicas) to the ring."""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        self.sorted_keys.sort()
        print(f"✅ Added {node}")

    def remove_node(self, node):
        """Remove a node from the ring."""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            if key in self.ring:
                del self.ring[key]
                self.sorted_keys.remove(key)
        print(f"❌ Removed {node}")

    def get_node(self, key):
        """Get the node responsible for the key."""
        if not self.ring:
            return None

        hashed_key = self._hash(key)

        # Linear search for simplicity (Binary Search is better for prod)
        for k in self.sorted_keys:
            if hashed_key <= k:
                return self.ring[k]

        # Wrap around to the first node
        return self.ring[self.sorted_keys[0]]

if __name__ == "__main__":
    # Create ring with 3 physical nodes, 3 replicas each
    ch = ConsistentHashing(["Node-A", "Node-B", "Node-C"], replicas=3)

    # Store some keys
    keys = ["User1", "User2", "User3"]
    print("\n--- Initial Mapping ---")
    for k in keys:
        print(f"Key '{k}' maps to -> {ch.get_node(k)}")

    # Add a new node
    print("\n--- Adding Node-D ---")
    ch.add_node("Node-D")

    # Check mapping again (Only some keys should move)
    print("\n--- New Mapping ---")
    for k in keys:
        print(f"Key '{k}' maps to -> {ch.get_node(k)}")
```

---

## 🧠 Interview Nuances

### 1. What is Sloppy Quorum?
*   Strict Quorum: Must write to the *intended* 3 nodes. If one is down, Write Fails.
*   Sloppy Quorum: Write to the *first 3 healthy* nodes. If intended node is down, write to a neighbor with a note ("This belongs to Node A"). When Node A returns, neighbor sends data back (**Hinted Handoff**).

### 2. How to detect failures?
*   **Gossip Protocol**: Each node picks 3 random nodes and shares "I am alive" + "I heard Node B is alive". Information propagates like a virus.

### 3. Merkle Trees?
*   A hash tree. Leaves are hashes of data blocks. Parent is hash of children.
*   To compare 1TB of data between Node A and Node B:
    *   Compare Root Hash. Same? Done (Data is identical).
    *   Different? Compare children. Drill down.
    *   Only transfer the specific block that differs.

---

## ⚡ Flashcards
1.  **CAP Theorem in Dynamo?**
    *   Dynamo chooses **AP** (Availability + Partition Tolerance). It sacrifices Strong Consistency for High Availability.
2.  **What are Virtual Nodes?**
    *   Assigning multiple positions on the hash ring to a single physical server. Improves load balancing and handles heterogeneous servers (stronger server gets more v-nodes).
3.  **Read Repair vs Anti-Entropy?**
    *   **Read Repair**: Fix data *during* a read request (Lazy).
    *   **Anti-Entropy**: Background process (Merkle Tree) to sync data (Active).
