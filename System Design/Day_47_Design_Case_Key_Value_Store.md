# Day 47: Design Case - Distributed Key-Value Store

## 🎯 Goal
Design a highly available Key-Value store like DynamoDB, Cassandra, or Riak.
**Focus**: CAP Theorem, Consistency Models, and Replication.

---

## 🗣️ Requirements

### Functional
1.  **put(key, value)**: Store data.
2.  **get(key)**: Retrieve data.
3.  **Configurable Consistency**: Allow users to choose Strong vs Eventual consistency.

### Non-Functional
1.  **High Availability**: System works even if nodes fail.
2.  **Scalability**: Linear scale with more nodes.
3.  **Fault Tolerance**: No single point of failure.

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: Simple modulo hashing (`hash(k) % N`) moves 100% of keys when N changes.
*   **Solution**: **Consistent Hashing** (Ring).
    *   Keys and Servers map to a point on a circle (0-2^32).
    *   Key maps to the first server clockwise.
    *   **Virtual Nodes**: To balance load, map each physical server to 100 virtual points on the ring.

### 2. Replication: Preference List
*   To ensure availability, data isn't just on one node.
*   Store key on the coordinator node + next 2 nodes on the ring (Replication Factor N=3).

### 3. Consistency: Quorums (N, R, W)
*   **N**: Number of replicas (e.g., 3).
*   **W**: Write Quorum (Must write to W nodes to succeed).
*   **R**: Read Quorum (Must read from R nodes to succeed).
*   **Strong Consistency**: R + W > N. (e.g., N=3, W=2, R=2). Guarantee overlap.
*   **Eventual Consistency**: W=1 (Fast writes, risk reading old data).

### 4. Conflict Resolution: Vector Clocks
*   If network partitions occur, two clients might update "User A" at the same time.
*   **Last Write Wins (LWW)**: Uses timestamp. Simple but loses data.
*   **Vector Clocks**: Tracks version per node `[NodeA:1, NodeB:2]`. Detects conflicts and asks client to resolve.

---

## 🏗️ System Architecture

1.  **Client** connects to any node (Coordinator).
2.  **Coordinator** hashes key, finds the preference list (Top N nodes).
3.  **Write Path**:
    *   Coordinator sends "Put" to N nodes.
    *   Waits for W acks.
    *   Returns Success.
    *   *Hinted Handoff*: If a node is down, write to a temporary neighbor with a hint "Give this back to Node A when it's up".
4.  **Read Path**:
    *   Coordinator sends "Get" to N nodes.
    *   Waits for R responses.
    *   **Read Repair**: If Node A returns v1 and Node B returns v2, return v2 to client and update Node A in background.

---

## 💻 Code Simulation: Consistent Hashing

Demonstrating how adding a node only moves a subset of keys.

```python
import hashlib

class ConsistentHashing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = {} # hash -> node_name
        self.sorted_keys = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # MD5 for simplicity
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        self.sorted_keys.sort()
        print(f"✅ Added Node: {node}")

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

        # Binary Search for the next highest key
        # (Simulated with simple iteration for clarity)
        for k in self.sorted_keys:
            if key <= k:
                return self.ring[k]

        # Wrap around
        return self.ring[self.sorted_keys[0]]

if __name__ == "__main__":
    ch = ConsistentHashing(nodes=["Server A", "Server B", "Server C"])

    print("\n--- Distribution ---")
    items = ["user_1", "user_2", "user_3", "user_4", "user_5"]
    for item in items:
        print(f"Item {item} -> {ch.get_node(item)}")

    # Add a new server
    print("\n--- Scaling Up ---")
    ch.add_node("Server D")

    print("\n--- New Distribution (Minimal Movement) ---")
    for item in items:
        print(f"Item {item} -> {ch.get_node(item)}")
```

**Output:**
```
✅ Added Node: Server A
✅ Added Node: Server B
✅ Added Node: Server C

--- Distribution ---
Item user_1 -> Server B
Item user_2 -> Server B
Item user_3 -> Server A
Item user_4 -> Server A
Item user_5 -> Server B

--- Scaling Up ---
✅ Added Node: Server D

--- New Distribution (Minimal Movement) ---
Item user_1 -> Server B
Item user_2 -> Server D (Only this changed!)
Item user_3 -> Server D (Only this changed!)
Item user_4 -> Server A
Item user_5 -> Server B
```

---

## 🧠 Interview Nuances

### 1. Anti-Entropy (Merkle Trees)
*   Replicas can drift out of sync silently.
*   **Merkle Tree**: A hash tree of the data. Nodes exchange Merkle Roots.
*   If Roots match -> Data is same.
*   If different -> Traverse down to find exactly which bucket is different and sync only that.

### 2. Tunable Consistency
*   "Sloppy Quorum": If main replicas are down, write to *anyone* (to maximize availability), but mark it.
*   This is AP (Availability > Partition Tolerance) in CAP.

### 3. Gossip Protocol
*   How do nodes know who is alive?
*   Nodes randomly tell 3 other nodes "I'm alive" every second. Information spreads like a virus (epidemic).

---

## ⚡ Flashcards
1.  **What is a Virtual Node?**
    *   A technique in Consistent Hashing where one physical server appears at multiple points on the ring to smooth out load distribution.
2.  **What is Read Repair?**
    *   Fixing data inconsistencies during the read process (Client sees mismatch -> System updates stale node).
3.  **Quorum Formula?**
    *   R + W > N (for strong consistency).
