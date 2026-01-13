# Day 47: Design Case - Distributed Key-Value Store

## 🎯 Goal
Design a highly available, scalable Key-Value store similar to **Amazon Dynamo** or **Apache Cassandra**.
**Focus**: Partitioning, Replication, and Consistency Models (CAP Theorem).

---

## 🗣️ Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Scalability**: Must handle massive data (Petabytes) and throughput (Millions QPS).
3.  **Configurable**: Tunable consistency (Strong vs Eventual).

### Non-Functional
1.  **High Availability**: The system should always accept writes (AP over CP).
2.  **Fault Tolerance**: No single point of failure.
3.  **Low Latency**: P99 < 20ms.

---

## 📐 Capacity Estimation
*   **Scale**: 100TB data.
*   **Node Capacity**: 2TB per node -> 50 nodes minimum.
*   **Replication Factor (N)**: 3 -> Total 150 nodes.

---

## 🧠 Core Design Decisions

### 1. Partitioning (Sharding)
*   **Problem**: How to distribute keys across 150 nodes?
*   **Modulo Hashing**: `hash(key) % N`. Bad, because adding a node reshuffles ALL keys.
*   **Solution**: **Consistent Hashing**.
    *   Map nodes to a ring (0 to $2^{64}$).
    *   Map keys to the ring.
    *   Key belongs to the first node found clockwise.
    *   **Virtual Nodes**: Each physical node appears at multiple points on the ring to balance load.

### 2. Replication
*   Replicate data to $N$ nodes (Preference List).
*   Typically, the "Coordinator" node replicates to the next $N-1$ nodes on the ring.

### 3. Consistency (Quorums)
*   **W**: Minimum nodes that must acknowledge write.
*   **R**: Minimum nodes that must respond to read.
*   **Formula**: If $W + R > N$, we have **Strong Consistency**.
*   **Common Config (Dynamo/Cassandra)**:
    *   $N=3, W=1, R=1$ (Fast, Eventual Consistency).
    *   $N=3, W=2, R=2$ (Strong Consistency, slower).

### 4. Conflict Resolution
*   If $W=1$, two nodes might have different versions of Key X.
*   **Last Write Wins (LWW)**: Use timestamp. (Cassandra default). Simple but can lose data.
*   **Vector Clocks**: Track version history `[NodeA:1, NodeB:2]`. Returns "siblings" (conflicts) to client to resolve. (Riak/Dynamo).

### 5. Storage Engine
*   **LSM Tree (Log-Structured Merge Tree)**:
    *   Write to Memory (MemTable).
    *   Flush to Disk (SSTable).
    *   Compaction merges SSTables in background.
    *   Optimized for **Write-Heavy** workloads.

---

## 🏗️ System Architecture

1.  **Client**: Connects to *any* node (acting as Coordinator).
2.  **Coordinator Node**:
    *   Hashes key to find partition.
    *   Forwards request to $N$ replicas.
    *   Waits for $W$ or $R$ acks.
3.  **Nodes**: Store data in MemTable/SSTable.
4.  **Gossip Protocol**: Nodes periodically exchange state ("I am alive", "Node X is dead").
5.  **Merkle Trees**: Used for "Anti-Entropy" (Repair) to compare data between replicas efficiently.

---

## 💻 Code Simulation: Consistent Hashing

Simulating the ring topology and key placement.

```python
import hashlib
import bisect

class ConsistentHashing:
    def __init__(self, num_replicas=3):
        self.ring = {} # hash_value -> node_name
        self.sorted_keys = []
        self.num_replicas = num_replicas # Virtual nodes per physical node

    def _hash(self, key):
        # Using MD5 for deterministic hashing
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        print(f"➕ Adding Node: {node}")
        for i in range(self.num_replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node):
        print(f"➖ Removing Node: {node}")
        keys_to_remove = [k for k, v in self.ring.items() if v == node]
        for k in keys_to_remove:
            del self.ring[k]
            self.sorted_keys.remove(k)

    def get_node(self, key):
        if not self.ring: return None
        hash_val = self._hash(key)
        # Binary Search to find the first node to the right
        idx = bisect.bisect(self.sorted_keys, hash_val)
        if idx == len(self.sorted_keys):
            idx = 0 # Wrap around

        node_hash = self.sorted_keys[idx]
        return self.ring[node_hash]

if __name__ == "__main__":
    ch = ConsistentHashing(num_replicas=3)
    ch.add_node("Node_A")
    ch.add_node("Node_B")

    keys = ["user_100", "order_55", "item_99"]
    for k in keys:
        print(f"Key '{k}' -> {ch.get_node(k)}")

    ch.add_node("Node_C") # Reshuffling happens here
    print("--- Added Node_C ---")
    for k in keys:
        print(f"Key '{k}' -> {ch.get_node(k)}")
```

**Output:**
```
➕ Adding Node: Node_A
➕ Adding Node: Node_B
Key 'user_100' -> Node_A
Key 'order_55' -> Node_B
Key 'item_99' -> Node_A
--- Added Node_C ---
➕ Adding Node: Node_C
Key 'user_100' -> Node_A
Key 'order_55' -> Node_C  <-- Remapped to new node
Key 'item_99' -> Node_A
```

---

## 🧠 Interview Nuances

### 1. Hinted Handoff
*   What if a replica is down?
*   **Scenario**: Node A is down. Coordinator writes to Node D (temporary) with a "hint" that it belongs to A.
*   When A comes back, D sends the data to A.

### 2. Read Repair vs Anti-Entropy
*   **Read Repair**: When reading, if Coordinator sees Replica 2 has stale data (timestamp check), it updates Replica 2 immediately.
*   **Anti-Entropy**: Background process using Merkle Trees to sync data.

### 3. Tunable Consistency
*   Q: "We need fast writes, but reads can be slightly stale."
    *   A: Set W=1, R=1.
*   Q: "We need absolute truth."
    *   A: Set W=Quorum, R=Quorum.

---

## ⚡ Flashcards
1.  **What is a Bloom Filter?**
    *   Probabilistic data structure used to check if an element exists. "Definitely No" or "Maybe Yes". Used to avoid disk lookups in SSTables.
2.  **SSTable vs B-Tree?**
    *   **SSTable (LSM)**: Faster writes (append only). Good for Cassandra/RocksDB.
    *   **B-Tree**: Faster reads. Good for SQL/MongoDB.
3.  **What is the Gossip Protocol?**
    *   Epidemic protocol where nodes share state with random peers. Converges state (who is up/down) across the cluster in $O(\log N)$ rounds.
