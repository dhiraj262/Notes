# Day 47: Design Case - Key-Value Store (Dynamo/Cassandra)

## 🎯 Goal
Design a highly available and scalable Key-Value Store (like DynamoDB, Cassandra, or Riak).
**Focus**: Partitioning, Replication, Consistency Models, and Conflict Resolution.

---

## 🗣️ Requirements

### Functional
1.  **put(key, value)**: Store a value.
2.  **get(key)**: Retrieve a value.
3.  **Configurable Consistency**: Allow client to choose Strong or Eventual consistency.

### Non-Functional
1.  **High Availability**: System should continue to work even if nodes fail. (AP over CP).
2.  **Scalability**: Linear scalability. Support massive data.
3.  **Fault Tolerance**: Handle network partitions and disk failures.

---

## 🧠 Core Design Decisions

### 1. CAP Theorem Strategy
*   We choose **AP (Availability + Partition Tolerance)**.
*   We sacrifice Strong Consistency for High Availability. We accept Eventual Consistency.

### 2. Data Partitioning: Consistent Hashing
*   **Problem**: Simple `hash(key) % N` breaks when N changes (nodes added/removed).
*   **Solution**: **Consistent Hashing**.
    *   Map nodes and keys to a Ring (0 to 2^64 - 1).
    *   Key K is stored on the first node found moving clockwise.
    *   **Virtual Nodes**: To balance load, map one physical node to multiple points on the ring.

### 3. Replication
*   Data must be replicated to `N` nodes (e.g., N=3) for durability.
*   **Strategy**: Store key on the Coordinator node + next N-1 nodes on the ring.

### 4. Consistency: Quorums
*   Configurable by client: `W` (write quorum), `R` (read quorum), `N` (replicas).
*   **Strong Consistency**: If `W + R > N`.
*   **Eventual Consistency**: If `W + R <= N`. (Faster, but risk of stale data).

### 5. Conflict Resolution
*   If two nodes accept writes for the same key (network partition), we have a conflict.
*   **Last Write Wins (LWW)**: Use timestamp. Easy but can lose data.
*   **Vector Clocks**: Capture causality. Keep all versions and let client resolve.

---

## 🏗️ System Architecture

1.  **Client** sends `put(key, value)` to a Load Balancer.
2.  **Node (Coordinator)** receives request.
    *   Hashes key to find the "preference list" (top N nodes).
3.  **Write Path**:
    *   Coordinator sends data to N nodes in parallel.
    *   Waits for `W` acknowledgments.
    *   Returns Success to client.
4.  **Read Path**:
    *   Coordinator requests data from N nodes.
    *   Waits for `R` responses.
    *   **Read Repair**: If nodes return different versions, return the latest one to client and update the stale nodes in background.

---

## 💻 Code Simulation: Consistent Hashing Ring

Simulating how keys are mapped to nodes on a ring.

```python
import hashlib
import bisect

class ConsistentHashing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas # Virtual nodes per physical node
        self.ring = {} # Hash -> Node Name
        self.sorted_keys = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # MD5 returns 128-bit hash
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
            del self.ring[key]
            self.sorted_keys.remove(key)
        print(f"❌ Removed Node: {node}")

    def get_node(self, key_string):
        if not self.ring: return None

        hashed_key = self._hash(key_string)
        # Find first node with hash >= hashed_key
        idx = bisect.bisect_left(self.sorted_keys, hashed_key)

        # If we reached end of ring, wrap around to 0
        if idx == len(self.sorted_keys):
            idx = 0

        target_hash = self.sorted_keys[idx]
        return self.ring[target_hash]

if __name__ == "__main__":
    ch = ConsistentHashing(nodes=["Node_A", "Node_B", "Node_C"], replicas=3)

    keys = ["User_1", "User_2", "User_3", "Order_99"]

    print("\n--- Distribution ---")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' mapped to -> {node}")

    ch.remove_node("Node_B")

    print("\n--- After removing Node_B ---")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' mapped to -> {node}")
```

**Output:**
```
✅ Added Node: Node_A
✅ Added Node: Node_B
✅ Added Node: Node_C

--- Distribution ---
Key 'User_1' mapped to -> Node_B
Key 'User_2' mapped to -> Node_A
Key 'User_3' mapped to -> Node_C
Key 'Order_99' mapped to -> Node_B

--- After removing Node_B ---
❌ Removed Node: Node_B
Key 'User_1' mapped to -> Node_C  <-- Remapped from B to C
Key 'User_2' mapped to -> Node_A  <-- Unchanged
Key 'User_3' mapped to -> Node_C  <-- Unchanged
Key 'Order_99' mapped to -> Node_C <-- Remapped from B to C
```

---

## 🧠 Interview Nuances

### 1. Gossip Protocol
*   How do nodes know if other nodes are alive?
*   Nodes periodically exchange state information with random peer nodes.
*   Information propagates like a virus (epidemic protocol).

### 2. Hinted Handoff
*   If a node is down, the coordinator sends the write to a "temp" node with a hint ("This belongs to Node B").
*   When Node B comes back, the temp node hands off the data.
*   Ensures availability even during failures.

### 3. Anti-Entropy (Merkle Trees)
*   How to sync data between replicas efficiently?
*   Use **Merkle Trees** (Hash Trees). Compare root hashes. If different, traverse down to find exact difference.

---

## ⚡ Flashcards
1.  **What is a Virtual Node?**
    *   A technique in consistent hashing where one physical node is responsible for multiple ranges on the ring to ensure even load distribution.
2.  **Explain Quorum `W + R > N`.**
    *   If Write Quorum plus Read Quorum is greater than Replication Factor, we are guaranteed to read the latest write (Strong Consistency).
3.  **What is a Vector Clock?**
    *   A list of (Node, Counter) pairs associated with a data version to detect causal relationships and conflicts.
