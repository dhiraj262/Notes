# Day 33: Replication - Single, Multi, and Leaderless

## 🎯 Goal
Understand how to keep copies of data on multiple machines to ensure Availability and Durability.
**Focus**: The trade-offs between Consistency and Latency in replicated systems.

---

## 🧩 Key Concepts

### 1. Why Replicate?
*   **High Availability**: If one node fails, others can serve data.
*   **Latency**: Keep data geographically close to users (CDN concept).
*   **Read Scalability**: Distribute read queries across many replicas.

### 2. Single-Leader Replication (Master-Slave)
*   **Architecture**: One Leader (Master), Many Followers (Slaves).
*   **Writes**: Only go to the Leader.
*   **Reads**: Can go to Leader or Followers.
*   **Replication Flow**: Leader writes to local storage -> sends change log to followers -> followers apply changes.
*   **Pros**: Simple mental model. No write conflicts (only one source of truth).
*   **Cons**: Leader is a write bottleneck. If Leader fails, failover is complex.
*   **Examples**: MySQL, PostgreSQL, MongoDB (default).

### 3. Multi-Leader Replication (Master-Master)
*   **Architecture**: More than one node accepts writes.
*   **Use Case**: Multi-datacenter setups. User in US writes to US-Leader; User in EU writes to EU-Leader.
*   **Pros**: Write availability survives a datacenter outage. Low write latency (local writes).
*   **Cons**: **Write Conflicts**. If User A sets X=1 in US and User B sets X=2 in EU at the same time, who wins? Resolution logic (LWW, Vector Clocks) is hard.

### 4. Leaderless Replication (Dynamo-style)
*   **Architecture**: No leader. Client sends write to ANY node.
*   **Quorums**: To ensure consistency, we use `R + W > N`.
    *   `N`: Total replicas.
    *   `W`: Write quorum (nodes that must confirm write).
    *   `R`: Read quorum (nodes that must respond to read).
*   **Pros**: Extreme availability. No failover downtime.
*   **Cons**: Complexity. Read Repair and Anti-Entropy processes needed.
*   **Examples**: Cassandra, DynamoDB, Riak.

---

## 🧠 Synchronous vs Asynchronous Replication

### Synchronous
*   **Flow**: Leader waits for Follower confirmation before telling client "Success".
*   **Pros**: Strong Consistency. Zero data loss if Leader dies.
*   **Cons**: High Latency. If one follower hangs, the whole write hangs.

### Asynchronous (Most Common)
*   **Flow**: Leader writes locally, tells client "Success", then sends to followers in background.
*   **Pros**: Fast. Leader not slowed by followers.
*   **Cons**: **Replication Lag**. If Leader dies before sending changes, data is lost.

---

## ⚠️ The Trap: Replication Lag Problems
When reading from an Async Follower, you might see stale data.
1.  **Read-Your-Own-Writes**: User posts a comment, refreshes page, comment is missing (hasn't reached follower yet).
    *   *Fix*: Read user's own profile from Leader.
2.  **Monotonic Reads**: User sees time move backward (Read from updated Follower A, then stale Follower B).
    *   *Fix*: Pin user to a specific replica (Sticky Session).

---

## 💻 Code Simulation: Quorum Logic

Simulating a Leaderless write/read decision.

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.data = {}

    def write(self, key, value):
        self.data[key] = value
        return True

    def read(self, key):
        return self.data.get(key, None)

def write_quorum(nodes, key, value, w):
    success_count = 0
    for node in nodes:
        if node.write(key, value):
            success_count += 1

    if success_count >= w:
        print(f"Write Success! ({success_count}/{len(nodes)})")
        return True
    else:
        print("Write Failed")
        return False

def read_quorum(nodes, key, r):
    responses = []
    for node in nodes:
        val = node.read(key)
        if val is not None:
            responses.append(val)

    if len(responses) >= r:
        # Simple resolution: Return most common or latest (omitted logic)
        print(f"Read Success! Got {len(responses)} responses: {responses}")
        return responses[0]
    else:
        print("Read Failed")
        return None

# Setup
n1, n2, n3 = Node("A"), Node("B"), Node("C")
cluster = [n1, n2, n3]

# Write with W=2 (Majority)
write_quorum(cluster, "user:1", "Alice", 2)

# Simulate network partition (Node A loses data or reverts)
n1.data = {}

# Read with R=2
# Even though n1 is empty, n2 and n3 have data. Since 2 >= R, we succeed.
read_quorum(cluster, "user:1", 2)
```

---

## ⚡ Flashcards
1.  **What is a Split Brain?**
    *   When two nodes both think they are the Leader (usually due to network partition). They both accept writes, leading to massive data corruption.
2.  **What is Eventual Consistency?**
    *   The guarantee that if no new updates are made, eventually all replicas will converge to the same value.
3.  **LWW (Last Write Wins)?**
    *   A conflict resolution strategy based on timestamps. Dangerous because clock skew can cause data loss (newer write discarded because it had an older timestamp from a drifting clock).
