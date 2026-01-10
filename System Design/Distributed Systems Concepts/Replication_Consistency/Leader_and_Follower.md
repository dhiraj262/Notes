# 👑 Deep Dive: Leader and Follower

> **Category**: Replication & Consistency
> **Core Concept**: A single node (Leader) handles all writes to ensuring order, while other nodes (Followers) replicate the data for durability and read scaling.
> **Also Known As**: Master-Slave, Primary-Secondary.

---

## 1. The Concept

Most databases (MySQL, Postgres, MongoDB, Redis) use **Leader-Based Replication**.
1.  **Writes**: Client sends write to the **Leader**. Leader writes to local storage.
2.  **Replication**: Leader sends the change (Replication Log) to **Followers**.
3.  **Reads**: Client can read from Leader or (optionally) from Followers.

### Types of Replication
1.  **Synchronous**: Leader waits for Follower to ack before telling Client "Success".
    *   *Pro*: Zero Data Loss.
    *   *Con*: Slow. If Follower dies, Leader blocks (Availability hit).
2.  **Asynchronous**: Leader tells Client "Success" immediately, then sends to Follower in background.
    *   *Pro*: Fast. Leader not blocked by Follower.
    *   *Con*: **Data Loss**. If Leader crashes before sending log, the write is lost.
3.  **Semi-Synchronous**: Wait for *one* follower to ack (Quorum-like).

---

## 2. Interview Post-Mortem: "The Async Trap"

### 🛑 The Trap
**Scenario**: Designing a Banking Ledger.
**Candidate**: *"I'll use MySQL with Asynchronous Replication to ensure low latency."*

**The Kill Shot**: *"The Leader crashes 1ms after confirming the transaction to the user. The Follower (new Leader) promotes itself but doesn't have that transaction. The user just lost $1000. Is that acceptable?"*

### ✅ The Solution
For financial/critical data, you **must** use Synchronous Replication (or consensus like Raft/Paxos), accepting the latency penalty.
Alternatively, use **Chain Replication** (Write goes to Head -> Middle -> Tail -> Ack).

---

## 3. Replication Logs (How it works under the hood)

### A. Statement-Based
*   Leader logs SQL: `INSERT INTO users VALUES (NOW(), ...)`
*   **Problem**: Non-deterministic functions like `NOW()` or `RAND()` generate different values on Followers.

### B. Write-Ahead Log (WAL) Shipping
*   Leader logs low-level byte changes: "Bytes 10-20 in Page 42 changed to X".
*   **Problem**: Coupled to storage engine version. Cannot replicate from Postgres 12 to 13.

### C. Row-Based (Logical)
*   Leader logs logical data: "Row with ID 5: set name='Alice'".
*   **Best Practice**: Most modern systems (MySQL Binlog) use this.

---

## 4. Implementation (Chain Replication Concept)

A simplified Python simulation of a **Chain Replication** (Sync) setup.

```python
class Node:
    def __init__(self, name, next_node=None):
        self.name = name
        self.next_node = next_node
        self.data = {}

    def write(self, key, value):
        # 1. Write locally
        print(f"[{self.name}] Writing {key}={value}")
        self.data[key] = value

        # 2. Forward to next node (Chain)
        if self.next_node:
            return self.next_node.write(key, value)
        else:
            # I am the Tail. The write is durable.
            print(f"[{self.name}] Tail Reached. Acking.")
            return True

    def read(self, key):
        # Reads usually go to the Tail in Chain Replication for Strong Consistency
        return self.data.get(key)

# --- Test ---
tail = Node("Follower_2 (Tail)")
middle = Node("Follower_1", next_node=tail)
head = Node("Leader (Head)", next_node=middle)

# Write to Head
print("--- Start Write ---")
success = head.write("balance", 1000)
print(f"Write Success: {success}")

# Read from Tail
print(f"Read Tail: {tail.read('balance')}")
```

---

## ⚡ Flashcards
1.  **Q: What is "Split Brain"?**
    *   *A: When the network partitions and TWO nodes both believe they are the Leader, accepting conflicting writes.*
2.  **Q: How do you fix replication lag?**
    *   *A: You can't "fix" physics, but you can mitigate impact by using "Monotonic Read" consistency (User reads from same replica) or Parallel Replication.*
3.  **Q: What happens if a Follower falls too far behind?**
    *   *A: It might need to stop following and do a full "Snapshot Recovery" (copy entire DB) from the Leader.*
