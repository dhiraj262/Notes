# Day 43: Consistency Models

## 🎯 Goal
Understand the spectrum of consistency guarantees in distributed systems.
**Focus**: Strong vs Eventual vs Causal Consistency.

---

## 🧩 Key Concepts

### 1. Strong Consistency (Linearizability)
*   **Definition**: Once a write is confirmed, *all* subsequent reads (from any node) see that value.
*   **Analogy**: A single shared notebook. Only one person writes at a time. Everyone sees the ink immediately.
*   **Cost**: High Latency. Requires synchronous replication (waiting for all nodes to agree).
*   **Use Case**: Bank balances, Inventory counters.

### 2. Eventual Consistency
*   **Definition**: If no new writes happen, eventually all nodes will agree. In the meantime, you might read stale data.
*   **Analogy**: Updating your profile picture. Your friend in Tokyo might see the old one for 5 minutes.
*   **Cost**: Low Latency. Fire and forget.
*   **Use Case**: Social media feeds, Likes, Comments, DNS.

### 3. Causal Consistency
*   **Definition**: Events that are causally related must be seen in order. Unrelated events can be out of order.
*   **Scenario**:
    *   A posts: "I love Star Wars."
    *   B replies: "Me too!"
    *   *Problem*: If C sees B's reply *before* A's post, it makes no sense.
    *   *Fix*: Causal consistency ensures B is seen after A.
*   **Use Case**: Chat apps, Comment threads.

---

## 📊 Comparison Table

| Model | Latency | Availability (CAP) | Implementation | Example |
| :--- | :--- | :--- | :--- | :--- |
| **Strong** | High | Low (CP) | 2PC, Paxos, Raft | SQL, Etcd, ZooKeeper |
| **Eventual** | Low | High (AP) | Gossip Protocol, Async Replication | DNS, DynamoDB (default) |
| **Causal** | Medium | Medium | Vector Clocks | Cassandra (Tunable) |

---

## 💻 Code Simulation: Replication Lag

Simulating the delay between writing to a Master and reading from a Replica (Eventual Consistency).

```python
import time
import threading

class Database:
    def __init__(self):
        self.master_data = {}
        self.replica_data = {}

    def write_master(self, key, value):
        print(f"✍️  Written to Master: {key}={value}")
        self.master_data[key] = value
        # Trigger async replication
        threading.Thread(target=self._replicate, args=(key, value)).start()

    def read_replica(self, key):
        val = self.replica_data.get(key, "N/A")
        print(f"👓 Read from Replica: {key}={val}")

    def _replicate(self, key, value):
        # Simulate Network Lag
        time.sleep(1)
        self.replica_data[key] = value
        print(f"   ... (1s later) Replicated to Replica ...")

if __name__ == "__main__":
    db = Database()

    # 1. Update Profile
    db.write_master("username", "cool_guy_99")

    # 2. Immediately view profile (Hit Replica)
    db.read_replica("username")

    # 3. Wait a bit
    time.sleep(1.5)
    db.read_replica("username")
```

**Output:**
```
✍️  Written to Master: username=cool_guy_99
👓 Read from Replica: username=N/A
   ... (1s later) Replicated to Replica ...
👓 Read from Replica: username=cool_guy_99
```

---

## ⚠️ The Trap: "I want Strong Consistency Everywhere"
*   **Trap**: Choosing Strong Consistency "just to be safe".
*   **Reality**: It makes your system slow and fragile. If one node is slow, the write halts.
*   **The Fix**: Ask "Does it matter if this data is 1 second old?" (e.g., View count on a YouTube video). If not, use Eventual.

---

## ⚡ Flashcards

1.  **What is a "Read Your Own Writes" consistency?**
    *   A guarantee that if I update my profile, *I* will see the new one immediately, even if others don't. Implementation: Pin the user to a specific replica or read from Master for 1 minute after write.
2.  **What is a Vector Clock?**
    *   A metadata list attached to data `[NodeA: 1, NodeB: 2]` used to detect conflicts and causality in distributed systems.
3.  **What is Tunable Consistency?**
    *   Systems like Cassandra allow you to choose `W=1` (Fast, Unsafe) or `W=ALL` (Slow, Strong) per query.
