# ⏲️ Deep Dive: Lease

> **Category**: Coordination & Consensus
> **Core Concept**: A contract that grants ownership of a resource for a limited time.
> **Difference from Lock**: A Lock is indefinite (must be explicitly unlocked). A Lease expires automatically (safety against crash).

---

## 1. The Concept

In a distributed system, how do you ensure only ONE node is the Leader?
*   **Naive Approach**: Node A acquires a Lock. Node A crashes. The Lock is held forever. System halts.
*   **Lease Approach**: Node A acquires a Lease for 10 seconds.
    *   If Node A is healthy, it renews the Lease at T=5s.
    *   If Node A crashes, the Lease expires at T=10s. Node B can take over.

---

## 2. Interview Post-Mortem: "The Zombie Leader"

### 🛑 The Trap
**Scenario**: Job Scheduler.
**Candidate**: *"Leader puts a flag `is_leader=True` in the DB. Workers check this flag."*

**The Kill Shot**: *"The Leader sets the flag and then power fails. The flag stays True forever. No new leader is elected. The system is dead."*

### ✅ The Solution
Use a **TTL (Time To Live)** or Lease.
*   Leader writes `leader_id=A, expires_at=NOW()+10s`.
*   Leader must heartbeat every 5s to update `expires_at`.
*   If `NOW() > expires_at`, anyone can claim leadership.

---

## 3. Implementation (Python Logic)

```python
import time

class LeaseManager:
    def __init__(self):
        self.owner = None
        self.expiry = 0

    def acquire(self, node_id, duration=5):
        now = time.time()
        # If free OR owned by me OR expired
        if self.owner is None or self.owner == node_id or now > self.expiry:
            self.owner = node_id
            self.expiry = now + duration
            print(f"✅ {node_id} acquired lease until {self.expiry:.2f}")
            return True
        else:
            print(f"❌ {node_id} failed. Owned by {self.owner} until {self.expiry:.2f}")
            return False

# --- Test ---
lm = LeaseManager()

# Node A takes lease
lm.acquire("NodeA", duration=2)

# Node B tries immediately
lm.acquire("NodeB", duration=2)

# Wait for expiry
print("Sleeping 2.1s...")
time.sleep(2.1)

# Node B tries again
lm.acquire("NodeB", duration=2)
```

---

## 4. Production Realities

### A. Clock Skew (Danger)
*   Server A thinks it has the lease (Local Time < Expiry).
*   Server B thinks the lease expired (Local Time > Expiry).
*   **Result**: Two Leaders (Split Brain).
*   **Fix**: Use a central authority (ZooKeeper/Etcd) for the clock, or use **Fencing Tokens** (monotonically increasing version numbers) to reject writes from old leaders.

### B. Garbage Collection Pause
*   Node A checks lease: "I have 5 seconds left".
*   Node A enters Java GC Pause for 6 seconds.
*   Node A wakes up thinking "I'm still leader", but Node B has already taken over.
*   **Fix**: Check lease *again* immediately before critical action, or use Fencing.

---

## ⚡ Flashcards
1.  **Q: What is the main advantage of a Lease over a Lock?**
    *   *A: Availability. If the holder crashes, the resource is automatically released after the timeout.*
2.  **Q: How do you prevent a node from thinking it holds a lease when it has actually expired (due to GC pause)?**
    *   *A: Fencing Tokens. Every time a lease is granted, increment a version number. The storage rejects writes with old version numbers.*
3.  **Q: Where is this used?**
    *   *A: Google Chubby, Etcd, DHCP (IP allocation).*
