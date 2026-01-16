# Day 47: Design a Key-Value Store (Dynamo/Cassandra)

## 🎯 Goal
Design a highly available, scalable Key-Value store similar to Amazon Dynamo or Apache Cassandra. It must handle massive read/write workloads with tunable consistency.

## 📋 Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Scalability**: Must scale horizontally to hundreds of nodes.
3.  **Availability**: "Always writeable" (AP system preference).
4.  **Consistency**: Eventual consistency is acceptable; tunable (Strong vs Eventual).

### Non-Functional
1.  **Low Latency**: < 10ms for p99.
2.  **Fault Tolerance**: Nodes can die without data loss.
3.  **No Single Point of Failure**: Decentralized architecture (Leaderless).

## 🔢 Capacity Estimation

*   **Data**: 10 TB of data.
*   **Replication Factor**: 3 (Total Storage = 30 TB).
*   **Nodes**: If each node holds 1TB, we need 30+ nodes.

## 🏗️ Architecture Design

### 1. Data Partitioning (Consistent Hashing)
*   **Problem**: How to distribute keys across $N$ nodes? `hash(key) % N` breaks when $N$ changes.
*   **Solution**: **Consistent Hashing Ring**.
    *   Map nodes to points on a ring ($0$ to $2^{128}-1$).
    *   Map keys to the ring.
    *   Walk clockwise to find the first node (Coordinator).
    *   **Virtual Nodes**: Each physical node maps to multiple points on the ring to balance load.

### 2. Replication
*   **Strategy**: To ensure durability, replicate data to the Coordinator and the next $N-1$ nodes on the ring.
*   **Preference List**: The list of nodes responsible for storing a key.

### 3. Consistency (Quorums)
*   **Tunable**: $N$ = Replicas, $W$ = Write Quorum, $R$ = Read Quorum.
*   **Strong Consistency**: $R + W > N$. (e.g., $N=3, W=2, R=2$).
*   **Eventual Consistency**: $R + W \le N$. Fast writes ($W=1$), fast reads ($R=1$), but risk of stale data.

### 4. Conflict Resolution
*   **Vector Clocks**: If two writes happen simultaneously (partitioned network), we get siblings.
*   The client (or system) must reconcile these versions using Vector Clocks to determine causality.
*   **Last Write Wins (LWW)**: Timestamp based. Simpler but can lose data. Used by Cassandra.

### 5. Storage Engine
*   **LSM Trees (Log-Structured Merge Trees)**:
    *   Writes go to **MemTable** (RAM).
    *   Flushed to **SSTable** (Disk, Immutable).
    *   Compaction merges SSTables in background.
    *   Optimized for high write throughput.

## 🐍 Code Simulation
Python implementation of **Consistent Hashing** with Virtual Nodes.

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, replicas=3):
        """
        replicas: Number of virtual nodes per physical node
        """
        self.replicas = replicas
        self.ring = [] # List of (hash, node_name)
        self.nodes = set()

    def _hash(self, key):
        # Using MD5 for stable hashing (simulated)
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node_name):
        self.nodes.add(node_name)
        for i in range(self.replicas):
            virtual_node_key = f"{node_name}:{i}"
            h = self._hash(virtual_node_key)
            # Insert maintaining sorted order (Ring structure)
            bisect.insort(self.ring, (h, node_name))
        print(f"[Ring] Added {node_name}. Total segments: {len(self.ring)}")

    def remove_node(self, node_name):
        if node_name in self.nodes:
            self.nodes.remove(node_name)
            # Remove all virtual nodes associated with this node
            self.ring = [x for x in self.ring if x[1] != node_name]
            print(f"[Ring] Removed {node_name}. Total segments: {len(self.ring)}")

    def get_node(self, key):
        if not self.ring:
            return None
        h = self._hash(key)
        # Binary search for the first node with hash >= h
        idx = bisect.bisect_left(self.ring, (h, ""))

        # If we reached the end, wrap around to the first node (Ring topology)
        if idx == len(self.ring):
            idx = 0

        target_node = self.ring[idx][1]
        print(f"[Lookup] Key '{key}' (Hash {str(h)[:5]}...) mapped to -> {target_node}")
        return target_node

# --- Driver Code ---
if __name__ == "__main__":
    ring = ConsistentHashRing(replicas=3)
    ring.add_node("Node_A")
    ring.add_node("Node_B")
    ring.add_node("Node_C")

    # Keys should distribute
    k1 = "user_123"
    k2 = "user_456"
    k3 = "session_x"

    ring.get_node(k1)
    ring.get_node(k2)
    ring.get_node(k3)

    # Remove a node and see re-mapping
    ring.remove_node("Node_B")
    print("\n--- After removing Node_B ---")
    # Only keys previously mapped to B should move. Others stay.
    ring.get_node(k1)
    ring.get_node(k2)
```

## 🧠 Interview Nuances

### "The Trap": Hot Partitions
*   **Problem**: What if Justin Bieber's data is accessed 1000x more than others? One node gets overwhelmed.
*   **Solution**: **Virtual Nodes** help balance data, but for specific hot keys, use **consistent hashing with bounded load** or replicate the hot key to *more* nodes specifically (Micro-caching).

### "The Kill Shot": Anti-Entropy
*   **Challenge**: "How do replicas synchronize if they missed a write?"
*   **Solution**: **Merkle Trees**.
    *   A hash tree where leaves are data hashes.
    *   Nodes exchange Merkle Trees. If root hash matches, data is same. If not, traverse down to find exact bucket that differs. Efficient sync.

### "Production Realities"
*   **Gossip Protocol**: Nodes talk to peer nodes periodically ("I'm alive", "Node X is dead") to maintain the cluster state membership list without a central master (like Zookeeper). This makes it truly decentralized.

## ⚡ Flashcards
*   **Partitioning Algo?** -> Consistent Hashing.
*   **High Write Storage?** -> LSM Trees (MemTable -> SSTable).
*   **Consistency Tuning?** -> W + R > N (Strong).
*   **Detect Data Drift?** -> Merkle Trees.
