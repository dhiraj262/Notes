# 🗳️ Deep Dive: Quorum

> **Category**: Replication & Consistency
> **Core Concept**: Ensuring consistency in distributed systems by requiring a minimum number of votes ($R$ or $W$) for an operation to succeed.

---

## 1. The Concept

In a leaderless replication system (like DynamoDB or Cassandra), we don't have a single master. To ensure data correctness, we define:
*   $N$: **Replication Factor** (Total copies of data).
*   $R$: **Read Quorum** (Nodes that must agree on a Read).
*   $W$: **Write Quorum** (Nodes that must ack a Write).

### The Formula
For **Strong Consistency** (Read-Your-Writes), we must satisfy:
$$ R + W > N $$

*   *Why?* It guarantees that the Read Set and Write Set overlap by at least one node. The reader will always see the latest write.

---

## 2. Interview Post-Mortem: "The Speed Trap"

### 🛑 The Trap
**Interviewer**: *"We want extremely fast writes for our Logging Service. $N=3$."*
**Candidate**: *"Okay, let's set $W=1$ (Write to any node) and $R=1$ (Read from any node) for max speed."*

**The Failure**:
*   $1 + 1 \ngtr 3$.
*   You have created an **Eventual Consistency** system with high risk of **Stale Reads**. If user writes to Node A, and reads from Node C, they won't see the data.

### ✅ The Solution
Tune the parameters based on the requirement:
1.  **Read Heavy**: $R=2, W=2, N=3$ (Balanced).
2.  **Write Heavy (Analytics)**: $W=1$ (Fast), $R=3$ (Slow, but consistent).
3.  **High Availability (AP)**: $W=1, R=1$ (Fast, assume eventual consistency is okay).

---

## 3. Sloppy Quorum vs Strict Quorum

### Strict Quorum
*   You **MUST** write to the $N$ designated "Home Nodes" for that key.
*   If a Home Node is down, the write **fails**.
*   *Result*: High Consistency, Lower Availability.

### Sloppy Quorum (Hinted Handoff)
*   If a Home Node is down, you can write to **ANY** healthy node in the cluster (a temporary foster parent).
*   The foster node holds the data in a "Hinted Handoff" buffer.
*   When the Home Node comes back, the data is pushed back.
*   *Result*: High Availability, Lower Consistency (Risk of data loss if foster node dies before handoff).

---

## 4. Implementation (Python Simulation)

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.data = {} # Key -> (Value, Timestamp)

    def write(self, key, value, timestamp):
        # Last-Write-Wins (LWW) logic
        if key not in self.data or timestamp > self.data[key][1]:
            self.data[key] = (value, timestamp)
            return True
        return True # Ack even if old (idempotent)

    def read(self, key):
        return self.data.get(key, (None, 0))

class QuorumCoordinator:
    def __init__(self, nodes, N=3, R=2, W=2):
        self.nodes = nodes # List of Node objects
        self.N = N
        self.R = R
        self.W = W

    def write(self, key, value, timestamp):
        acks = 0
        # In real life, we pick specific N nodes based on Hash Ring
        # Here we broadcast to first N
        target_nodes = self.nodes[:self.N]

        for node in target_nodes:
            if node.write(key, value, timestamp):
                acks += 1

        if acks >= self.W:
            return True
        else:
            return False # Write Failure

    def read(self, key):
        responses = []
        target_nodes = self.nodes[:self.N]

        for node in target_nodes:
            val, ts = node.read(key)
            if val is not None:
                responses.append((val, ts))

        if len(responses) < self.R:
            return None # Read Failure

        # Read Repair / Conflict Resolution: Return latest timestamp
        responses.sort(key=lambda x: x[1], reverse=True)
        return responses[0][0] # Return value with highest timestamp

# --- Test ---
nodes = [Node("A"), Node("B"), Node("C")]
coord = QuorumCoordinator(nodes, N=3, R=2, W=2)

print(f"Write: {coord.write('user_1', 'John', 100)}") # Needs 2 acks
print(f"Read:  {coord.read('user_1')}")               # Needs 2 reads
```

---

## ⚡ Flashcards
1.  **Q: What is the downside of $W=N$ (Write All)?**
    *   *A: Availability is terrible. If even 1 node is down, the system cannot accept writes.*
2.  **Q: What is Read Repair?**
    *   *A: When reading with Quorum, if the coordinator notices Node A has `v2` and Node B has `v1`, it returns `v2` to the client AND asynchronously updates Node B with `v2`.*
3.  **Q: Does $R+W > N$ guarantee transactions (ACID)?**
    *   *A: No. It only guarantees strong consistency for single-key operations. It does not provide atomicity across multiple keys.*
