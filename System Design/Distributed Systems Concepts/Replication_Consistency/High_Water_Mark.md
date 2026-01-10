# 🌊 Deep Dive: High-Water Mark

> **Category**: Replication & Consistency
> **Core Concept**: An index (offset) in the replication log up to which data is safely replicated to a Quorum of followers and is visible to clients.

---

## 1. The Concept

In Leader-Follower replication (like Raft or Kafka), the Leader might have entries in its log that haven't been replicated yet.
The **High-Water Mark (HWM)** is the highest index that is **Committed** (safe).
*   **Clients**: Can only read up to the HWM.
*   **Followers**: If a follower crashes and rejoins, any data it has *beyond* the HWM (uncommitted data from a failed leader term) must be truncated.

---

## 2. Interview Post-Mortem: "The Ghost Data"

### 🛑 The Trap
**Scenario**: Designing a Replicated State Machine.
**Candidate**: *"Leader writes to disk, then immediately tells the client 'Success'. Then it replicates."*

**The Kill Shot**: *"The Leader crashes. A Follower becomes Leader. It didn't see that write. The old Leader comes back. It still has the write. Now we have **Divergent Logs**. The client thinks the write exists, but the new Leader says it doesn't."*

### ✅ The Solution
1.  Leader writes to local log.
2.  Replicate to Followers.
3.  Wait for **Majority Acknowledgement**.
4.  Advance **High-Water Mark**.
5.  *Then* reply "Success" to Client.
6.  If Old Leader rejoins, it sees its log is ahead of the Cluster HWM -> **Truncate** the uncommitted entries.

---

## 3. Implementation (Python Logic)

```python
class Follower:
    def __init__(self, name):
        self.name = name
        self.match_index = 0 # Highest log entry replicated here

class Leader:
    def __init__(self, followers):
        self.log_length = 0
        self.followers = followers
        self.commit_index = 0 # High-Water Mark

    def append_entry(self):
        self.log_length += 1
        print(f"Leader: Log at {self.log_length}")

    def receive_ack(self, follower_name, index):
        for f in self.followers:
            if f.name == follower_name:
                f.match_index = max(f.match_index, index)
                self.update_commit_index()
                break

    def update_commit_index(self):
        # Sort match_indices. The median (middle) is the value reached by Majority.
        # Example: [2, 2, 5, 5, 5] -> Majority is 5.
        # Example: [1, 2, 3] -> Median is 2.
        indexes = sorted([f.match_index for f in self.followers] + [self.log_length])
        mid = len(indexes) // 2
        new_commit = indexes[mid] # Simply logic for majority

        if new_commit > self.commit_index:
            self.commit_index = new_commit
            print(f"🌊 High-Water Mark advanced to: {self.commit_index}")

# --- Test ---
f1 = Follower("F1")
f2 = Follower("F2")
leader = Leader([f1, f2]) # Total 3 nodes (Leader + 2 Followers)

# Leader writes 5 entries
for _ in range(5): leader.append_entry()

# F1 syncs up to 5
leader.receive_ack("F1", 5)
# Majority is [0, 5, 5] (Leader=5, F1=5, F2=0) -> Median is 5.
# HWM should be 5.
```

---

## 4. Production Realities

### A. Consumer Lag
*   In Kafka, the consumer can only consume up to the HWM. Even if the leader has 1GB of new data, if the replicas are slow, the HWM stays low, and consumers see nothing. **Latency Spike**.

### B. Truncation
*   When a node rejoins, it must ask the current Leader: "What is the HWM?"
*   If the node has data at offset 101, but HWM is 100, the node **must delete** offset 101. It was never committed.

---

## ⚡ Flashcards
1.  **Q: What happens to data "above" the High-Water Mark?**
    *   *A: It is considered "Uncommitted" or "Dirty". Clients cannot read it. It may be lost/truncated if the leader fails.*
2.  **Q: Why do we need HWM?**
    *   *A: To prevent "Phantom Reads" where a client reads data that later disappears because it wasn't fully replicated.*
3.  **Q: In Kafka, what is the HWM called?**
    *   *A: The "HW" or Last Stable Offset.*
