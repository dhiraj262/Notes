# Day 43: Consistency Models

## 🎯 Goal
Understand the spectrum of consistency in distributed systems, from "Everyone sees the same thing instantly" to "Eventually everyone will agree."
**Focus**: Strong, Eventual, Causal Consistency, and the PACELC theorem.

---

## 🧩 Key Concepts

### 1. Strong Consistency (Linearizability)
*   **Definition**: Once a write is acknowledged, all subsequent reads (from any node) return the new value.
*   **Real World**: Bank Account balances.
*   **Cost**: High Latency (Must replicate to all nodes before Ack) & Low Availability (If one node is down, write might fail).
*   **Systems**: SQL Databases, CP systems (Zookeeper, Etcd).

### 2. Eventual Consistency
*   **Definition**: If no new updates are made, eventually all accesses will return the last updated value. Reads might return stale data for a while.
*   **Real World**: DNS, YouTube View Count, Facebook Likes.
*   **Benefit**: High Availability & Low Latency.
*   **Systems**: Cassandra, DynamoDB (configurable), DNS.

### 3. Causal Consistency
*   **Definition**: Operations that are causally related (A caused B) must be seen in that order. Unrelated operations can be seen in any order.
*   **Real World**: Chat replies. (You shouldn't see "Haha" before seeing the joke it replied to).

---

## 🏗️ PACELC Theorem
An extension of CAP Theorem.
*   **If Partition (P)**: Choose Availability (A) or Consistency (C).
*   **Else (E)** (Normal operation): Choose Latency (L) or Consistency (C).
*   *Meaning*: Even when the network is fine, you have to trade off speed vs correctness.
    *   **DynamoDB/Cassandra**: Tunable. `R=1, W=1` (Fast, inconsistent). `R=Quorum, W=Quorum` (Slow, consistent).

---

## 💻 Code Simulation: Quorum Consistency
A simulation of reading/writing to 3 nodes with configurable `R` and `W`.

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.data = 0 # Initial state

    def write(self, value):
        self.data = value
        return True

    def read(self):
        return self.data

nodes = [Node("N1"), Node("N2"), Node("N3")]

def write_quorum(value, w):
    success_count = 0
    for node in nodes:
        if node.write(value):
            success_count += 1
            if success_count >= w:
                return True
    return False

def read_quorum(r):
    values = []
    # Simulate reading from first 'r' available nodes
    # In reality, we'd read timestamps and return the latest
    for i in range(r):
        values.append(nodes[i].read())

    # Return the most frequent or max version
    return max(set(values), key=values.count)

# Simulation
# Scenario: W=2, R=2 (Strong Consistency because W+R > N)
# N=3.
print("Writing 100 to 2 nodes...")
write_quorum(100, 2)
# Note: Node 3 might still have 0.

print(f"Reading from 2 nodes: {read_quorum(2)}")
```

---

## ⚠️ The Trap: "Read Your Own Writes"
*   **Problem**: User posts a comment (Write to Leader), page refreshes (Read from Follower). Follower hasn't synced yet. User thinks comment is lost.
*   **The Fix**: **Stickiness**.
    *   If a user modified data recently, force their reads to go to the Leader (or the same replica they wrote to) for X minutes.

---

## ⚡ Flashcards
1.  **What is a Sloppy Quorum?**
    *   In systems like Dynamo, if preferred nodes are down, write to *any* healthy node (hinted handoff) to satisfy W. Increases availability but risks consistency.
2.  **Equation for Strong Consistency?**
    *   `W + R > N`. (Write nodes + Read nodes > Total nodes).
    *   Guarantees at least one node in the Read set has the latest Write.
3.  **Monotonic Read Consistency?**
    *   Guarantee that if a user sees a value, they will never see an older value in subsequent reads.
