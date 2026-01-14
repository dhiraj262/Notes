# Day 47: Design Case - Distributed Key-Value Store

## 🎯 Goal
Design a highly available and scalable Key-Value Store (like DynamoDB, Cassandra, or Riak).
**Focus**: CAP Theorem, Consistent Hashing, and Replication.

---

## 🗣️ Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Scalability**: Must handle massive data (Petabytes) and high throughput.
3.  **Configurable Consistency**: Allow users to choose Strong (Read-your-writes) or Eventual Consistency.

### Non-Functional
1.  **High Availability**: System should continue to accept writes even if some nodes are down (AP system).
2.  **Fault Tolerance**: No single point of failure.
3.  **Low Latency**: < 10ms for reads/writes.

---

## 📐 Capacity Estimation
*   **Throughput**: 10 Million operations/sec.
*   **Data**: 100 TB.
*   **Architecture**: Shared-Nothing (Peer-to-Peer).

---

## 🧠 Core Design Decisions

### 1. Data Partitioning: Consistent Hashing
*   **Problem**: With `hash(key) % N`, adding a server requires re-shuffling ALL keys.
*   **Solution**: **Consistent Hashing** (Ring topology).
    *   Map servers to points on a circle (0-360 degrees).
    *   Map keys to points. Key belongs to the first server clockwise.
    *   **Virtual Nodes**: Each server appears multiple times on the ring to balance load.
    *   Benefit: Adding/Removing a node only affects neighbors.

### 2. Replication (N)
*   To ensure availability, data must be copied.
*   **Strategy**: Replicate key to the coordinator node AND the next N-1 nodes on the ring.
*   **Preference Lists**: Each key has a specific list of nodes that store it.

### 3. Consistency (W, R) - Quorum
*   **N**: Number of replicas (e.g., 3).
*   **W**: Write quorum. How many nodes must acknowledge write?
*   **R**: Read quorum. How many nodes must respond to read?
*   **Strong Consistency**: W + R > N. (e.g., N=3, W=2, R=2. 2+2 > 3).
*   **Eventual Consistency**: W + R <= N. (Fast, but risk of stale data).

### 4. Conflict Resolution
*   If two nodes accept writes for the same key at the same time (Network Partition), we have a conflict.
*   **Solution**: Vector Clocks or Last-Write-Wins (LWW).

---

## 🏗️ System Architecture

1.  **Client** uses a library that knows the Hash Ring configuration.
2.  **Client** hashes Key -> determines **Coordinator Node**.
3.  **Coordinator**:
    *   For **Write**: Sends data to N replicas. Waits for W acks.
    *   For **Read**: Requests data from N replicas. Waits for R responses. Uses Versioning to reconcile diffs.
4.  **Gossip Protocol**: Nodes periodically "gossip" with random peers to detect failures (Heartbeat).
5.  **Hinted Handoff**: If a node is down, the neighbor temporarily stores the write and replays it when the node returns.

---

## 💻 Code Simulation: Consistent Hashing

Simulating how keys are mapped to nodes and how they move when nodes are added/removed.

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, num_replicas=3):
        self.ring = [] # List of (hash, node_name)
        self.num_replicas = num_replicas

    def _hash(self, key):
        """Returns a large integer hash for the key"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        """Adds a node (and its virtual replicas) to the ring"""
        for i in range(self.num_replicas):
            virtual_node_name = f"{node}#{i}"
            key = self._hash(virtual_node_name)
            # Insert while keeping sorted
            bisect.insort(self.ring, (key, node))
        print(f"✅ Added Node: {node}")

    def remove_node(self, node):
        """Removes a node and its replicas"""
        self.ring = [x for x in self.ring if x[1] != node]
        print(f"❌ Removed Node: {node}")

    def get_node(self, key):
        """Finds the node responsible for a key"""
        if not self.ring:
            return None

        hash_val = self._hash(key)
        # Binary search for the first node with hash >= key hash
        # We search based on the first element of tuple (hash)

        # Extract keys for bisect
        keys = [x[0] for x in self.ring]
        idx = bisect.bisect_right(keys, hash_val)

        # If we reach end of ring, wrap around to 0
        if idx == len(self.ring):
            idx = 0

        return self.ring[idx][1]

if __name__ == "__main__":
    ch = ConsistentHashRing(num_replicas=3)

    # 1. Add Servers
    ch.add_node("Server_A")
    ch.add_node("Server_B")
    ch.add_node("Server_C")

    # 2. Distribute Keys
    keys = ["user_1", "user_2", "user_3", "order_99", "image_jpg"]
    print("\n--- Initial Distribution ---")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' mapped to -> {node}")

    # 3. Add a new Server (Scaling up)
    print("\n--- Scaling Up: Adding Server_D ---")
    ch.add_node("Server_D")

    # Check re-mapping (Only some keys should move)
    print("Checking keys again:")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' mapped to -> {node}")

    # 4. Remove a Server (Failure)
    print("\n--- Failure: Removing Server_A ---")
    ch.remove_node("Server_A")
    for k in keys:
        node = ch.get_node(k)
        print(f"Key '{k}' mapped to -> {node}")
```

**Output:**
```
✅ Added Node: Server_A
✅ Added Node: Server_B
✅ Added Node: Server_C

--- Initial Distribution ---
Key 'user_1' mapped to -> Server_B
Key 'user_2' mapped to -> Server_B
Key 'user_3' mapped to -> Server_C
Key 'order_99' mapped to -> Server_C
Key 'image_jpg' mapped to -> Server_C

--- Scaling Up: Adding Server_D ---
✅ Added Node: Server_D
Checking keys again:
Key 'user_1' mapped to -> Server_B
Key 'user_2' mapped to -> Server_B
Key 'user_3' mapped to -> Server_D
Key 'order_99' mapped to -> Server_D
Key 'image_jpg' mapped to -> Server_C

--- Failure: Removing Server_A ---
❌ Removed Node: Server_A
Key 'user_1' mapped to -> Server_B
Key 'user_2' mapped to -> Server_B
Key 'user_3' mapped to -> Server_D
Key 'order_99' mapped to -> Server_D
Key 'image_jpg' mapped to -> Server_C
```

---

## 🧠 Interview Nuances

### 1. What is "Sloppy Quorum"?
*   If Node A is down, the system writes to Node D (who is not in the usual preference list) with a "hint" to send it back to A later. This ensures Availability (write succeeds) even if N replicas aren't strictly met.

### 2. How to detect data corruption?
*   **Merkle Trees**: A hash tree where leaves are hashes of data blocks. Nodes compare Merkle Root hashes. If different, they traverse down to find the specific bucket that differs and sync only that.

### 3. Tunable Consistency?
*   For a payment system: Set W=3, R=1 (Strong Write).
*   For a "Likes" counter: Set W=1, R=1 (Fast, eventual).

---

## ⚡ Flashcards
1.  **What is the "Coordinator Node"?**
    *   The node that handles the incoming request (usually the first node in the preference list for that key).
2.  **Vector Clocks vs Timestamp?**
    *   Timestamps (LWW) are simple but can lose data if clocks drift. Vector Clocks catch conflicts (e.g., two people editing same doc) but are complex to merge.
3.  **Anti-Entropy?**
    *   The process of comparing replicas and updating them to be identical (using Merkle Trees).
