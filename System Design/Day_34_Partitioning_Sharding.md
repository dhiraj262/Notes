# Day 34: Partitioning (Sharding)

## 🎯 Goal
Understand how to split a large dataset across multiple machines when it no longer fits on one.
**Focus**: Strategies for breaking data apart and the complexities it introduces.

---

## 🧩 Key Concepts

### 1. Why Partition?
*   **Scalability**: Store more data than a single disk can hold.
*   **Throughput**: Distribute read/write load across many processors.

### 2. Partitioning Strategies

#### A. Key-Range Partitioning
*   **Logic**: Assign ranges of keys to nodes. E.g., Keys A-F -> Node 1, G-M -> Node 2.
*   **Pros**: Efficient Range Queries (e.g., "Get all users created in 2023").
*   **Cons**: **Hot Spots**. If keys are timestamps, all writes today go to ONE node.
*   **Example**: HBase, BigTable.

#### B. Hash Partitioning (Key-Based)
*   **Logic**: `Partition = Hash(Key) % N`.
*   **Pros**: Distributes load evenly (Uniform Distribution). Eliminates hot spots (mostly).
*   **Cons**: **Range queries are impossible**. To find "users created today", you must query ALL partitions (Scatter-Gather).
*   **Example**: Cassandra, DynamoDB, MongoDB (hashed sharding).

---

## 🧠 The "Hot Key" Problem (Skew)
Even with Hash Partitioning, a single key can be too popular.
*   **Scenario**: Justin Bieber tweets. Millions of people reply to that ONE tweet ID.
*   **Result**: The node holding that Tweet ID gets hammered.
*   **The Fix**:
    *   **Salting**: Append a random number to the key. `Bieber_Tweet` becomes `Bieber_Tweet_1`, `Bieber_Tweet_2`.
    *   Writes are split across nodes.
    *   Reads must query all split keys and aggregate.

---

## 🛠️ Rebalancing & Consistent Hashing
When you add a new node, you need to move data.
*   **Mod N Problem**: If you use `Hash % N`, changing N changes the result for almost all keys. Massive data transfer ensues.
*   **Solution**: **Consistent Hashing** (covered in Day 32, but critical here).
    *   Only move data from the immediate neighbor on the ring.
    *   **Virtual Nodes**: To prevent nonuniform distribution, each physical node represents multiple "virtual" points on the ring.

---

## 💻 Code Simulation: Range vs Hash

```python
import hashlib

data = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
nodes = ["Node1", "Node2"]

print("--- Range Partitioning (A-M, N-Z) ---")
for name in data:
    first_char = name[0].upper()
    if first_char < 'N':
        print(f"{name} -> Node1")
    else:
        print(f"{name} -> Node2")

print("\n--- Hash Partitioning (Mod 2) ---")
for name in data:
    # Hash name to integer
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    node_idx = h % len(nodes)
    print(f"{name} -> {nodes[node_idx]}")
```

**Observation**:
*   If we had names ["Aaron", "Abby", "Adam"], Range Partitioning would dump them all on Node 1 (Skew).
*   Hash Partitioning would likely scatter them.

---

## 🧠 Interview Nuances

### Secondary Indexes
If you shard by `UserId`, but want to search by `Email`, what happens?
1.  **Local Secondary Index (Document Partitioned)**: Each partition keeps an index of its own data.
    *   *Query*: "Find email X" -> Must query ALL partitions (Scatter-Gather). Expensive read.
2.  **Global Secondary Index (Term Partitioned)**: A separate dedicated partition holds the email index.
    *   *Query*: "Find email X" -> Go to Index Partition, find UserId, go to User Partition. Fast read.
    *   *Write*: Slow. Writing a user updates User Partition AND Index Partition (Distributed Tx).

---

## ⚡ Flashcards
1.  **What is Scatter-Gather?**
    *   When a query needs data from all partitions, the coordinator sends the request to all of them, waits for responses, and aggregates the results.
2.  **Does Sharding affect ACID?**
    *   Yes. Transactions within a single shard are easy. Transactions across shards require 2PC (Two-Phase Commit) which kills performance.
3.  **What is Directory-Based Partitioning?**
    *   A lookup service knows exactly which node holds which key. Highly flexible but the lookup service is a SPOF and bottleneck.
