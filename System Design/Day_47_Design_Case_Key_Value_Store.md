# Day 47: Design Case - Key-Value Store (Dynamo/Cassandra)

## 🎯 Goal
Design a highly available Key-Value store similar to Amazon Dynamo or Cassandra.
**Focus**: Partitioning, Replication, and Tunable Consistency.

---

## 🗣️ Requirements

### Functional
1.  **Operations**: `put(key, value)` and `get(key)`.
2.  **Scalability**: Must handle massive data and throughput.
3.  **Availability**: "Always Writeable" (AP system).

### Non-Functional
1.  **Low Latency**: Read/Write < 10ms.
2.  **Fault Tolerance**: Server failures should not lose data.
3.  **Tunable Consistency**: Allow user to choose Strong vs Eventual consistency.

---

## 📐 Capacity Estimation
*   **Data**: 100 TB.
*   **Replication Factor**: 3. Total Storage = 300 TB.
*   **Node Capacity**: 2TB per node. Need ~150 nodes.

---

## 🏗️ System Architecture

### 1. Data Partitioning (Consistent Hashing)
*   Use a **Hash Ring**.
*   Nodes are placed on the ring.
*   Key is hashed -> placed on ring -> stored in the first node clockwise.
*   **Virtual Nodes**: To balance load, each physical node appears as `k` virtual nodes on the ring.

### 2. Replication
*   Replicate data to `N` successive nodes on the ring (Preference List).
*   Typically `N=3`.
*   **Sloppy Quorum**: If Node A is down, write to Node D (hinted handoff). When A comes back, D sends data back.

### 3. Consistency (Quorums)
*   **N**: Replication Factor (e.g., 3).
*   **W**: Write Quorum (Min acks needed for write success).
*   **R**: Read Quorum (Min responses needed for read success).
*   **Rule**: `R + W > N` implies Strong Consistency.
    *   Example: N=3, W=2, R=2. (2+2 > 3).
*   **Eventual Consistency**: W=1 (Fast write).

### 4. Conflict Resolution (Vector Clocks)
*   Since we allow writes on any replica (Leaderless), conflicts happen.
*   Use **Vector Clocks** to detect causality.
*   If conflicts (concurrent writes), return both versions to client -> **Client resolves**.

---

## 💻 Code Simulation: Quorum Logic

Simulating the concept of W and R parameters.

```python
class KeyValueStore:
    def __init__(self):
        self.store = {}

    def put(self, key, value, consistency_level="ALL"):
        # Simulate replication to 3 nodes
        print(f"📝 Writing {key}={value}...")
        self.store[key] = value
        # In real system: wait for W acks
        print(f"   ✅ Replicated to Node 1, Node 2, Node 3")

    def get(self, key, consistency_level="ONE"):
        if key in self.store:
            print(f"🔍 Found {key}: {self.store[key]}")
            return self.store[key]
        else:
            print(f"❌ {key} not found")
            return None

if __name__ == "__main__":
    kv = KeyValueStore()

    kv.put("user:1", "Alice")
    kv.get("user:1")
    kv.get("user:2")
```

**Output:**
```
📝 Writing user:1=Alice...
   ✅ Replicated to Node 1, Node 2, Node 3
🔍 Found user:1: Alice
❌ user:2 not found
```

---

## 🧠 Interview Nuances

### 1. Gossip Protocol
*   How do nodes know who is alive?
*   Nodes randomly exchange state information with peers. Infection spreads fast (O(log N)).

### 2. Anti-Entropy (Merkle Trees)
*   How to fix data discrepancies between replicas?
*   Compare **Merkle Trees** (Hash trees) of data. Only exchange parts of the tree that differ.

### 3. Storage Engine
*   **LSM Trees** (Log Structured Merge Trees).
*   Fast Writes (Append only).
*   Compaction processes merge logs in background.

---

## ⚡ Flashcards
1.  **What is a Virtual Node?**
    *   A technique in Consistent Hashing where one physical node handles multiple ranges on the ring to improve load balancing.
2.  **What is Hinted Handoff?**
    *   If a target node is down, the system temporarily writes to another node with a note ("hint") to send it back when the target recovers.
3.  **LSM Tree vs B-Tree?**
    *   LSM: Optimizes for Write throughput (Sequential writes). Used in Cassandra/RocksDB.
    *   B-Tree: Optimizes for Read throughput. Used in MySQL/Postgres.
