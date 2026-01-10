# 🔄 System Design Deep Dive: Consistent Hashing

**Context**: An analysis of data partitioning strategies. Why `Modulo N` fails in dynamic environments and how Consistent Hashing with Virtual Nodes solves the "Re-hashing Storm".
---

## 1. The Trap: "Just use Modulo N"

**The Scenario**: You are designing a Distributed Cache or a Sharded Database. The interviewer asks, *"How do we decide which server stores User A's data?"*
You answer: *"Simple! We hash the User ID and take modulo N (number of servers)."*

$$ \text{Server Index} = \text{hash(user\_id)} \% N $$

**The Kill Shot**: *"Great. We have 10 servers. We are overwhelmed and need to add 2 new servers. What happens to the data?"*

**The Failure**: You realize that when $N$ changes from 10 to 12, the result of $hash(k) \% 10$ is completely different from $hash(k) \% 12$.

### 💥 The Math of the Disaster
*   **Reshuffling**: With Modulo hashing, changing $N$ causes nearly **100% of keys to move** (specifically $1 - 1/N$ don't move, but effectively everything churns).
*   **Thundering Herd**: Your cache hit rate drops to 0%. All requests hit the database. The database melts. The site goes down.

---

## 2. The Solution: Consistent Hashing (The Ring)

**Concept**: Instead of mapping keys to servers, we map **both** servers and keys onto a common **Ring** (range $0$ to $2^{32}-1$).

**The Rule**:
1.  Hash each **Server** (IP or ID) to a point on the ring.
2.  Hash the **Key** to a point on the ring.
3.  To find the server for a key, move **clockwise** on the ring until you find a server.

**Why it works**:
*   **Adding a Node**: If we add Server X, it lands between Server A and Server B. It only "steals" the keys that were previously assigned to B (those falling between A and X).
*   **Impact**: Only $K/N$ keys need to move. The rest of the system is untouched.

---

## 3. The Implementation: Python + Virtual Nodes

**The "Virtual Node" Twist**:
*   *Problem*: If you have only 3 servers, they might clump together on the ring, causing uneven load (Data Skew).
*   *Fix*: **Virtual Nodes**. One physical server is represented by $k$ (e.g., 100) points on the ring. This ensures uniform distribution.

### 🐍 Code: Ring with Virtual Nodes

We use `bisect` (Binary Search) to find the nearest server efficiently ($O(\log N)$).

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, nodes=None, replicas=3):
        """
        :param nodes: List of physical server names (e.g., ['10.0.0.1', '10.0.0.2'])
        :param replicas: Number of virtual nodes per physical node (higher = better distribution)
        """
        self.replicas = replicas
        self.ring = {}          # Maps Hash -> Physical Node
        self.sorted_keys = []   # Sorted list of Hashes for Binary Search

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        """Returns a 0-2^128 integer hash (MD5)"""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        """Adds a physical node (and its virtual replicas) to the ring"""
        for i in range(self.replicas):
            # Create virtual node name: "node_ip#1", "node_ip#2"...
            virtual_key = f"{node}#{i}"
            key_hash = self._hash(virtual_key)

            self.ring[key_hash] = node
            bisect.insort(self.sorted_keys, key_hash)

    def remove_node(self, node):
        """Removes a physical node and all its replicas"""
        for i in range(self.replicas):
            virtual_key = f"{node}#{i}"
            key_hash = self._hash(virtual_key)

            if key_hash in self.ring:
                del self.ring[key_hash]
                # Note: removing from sorted list is O(N), acceptable for infrequent config changes
                self.sorted_keys.remove(key_hash)

    def get_node(self, key):
        """Finds the server for a given key (Clockwise search)"""
        if not self.ring:
            return None

        key_hash = self._hash(key)

        # Binary Search: Find the first hash >= key_hash
        idx = bisect.bisect_left(self.sorted_keys, key_hash)

        # If we hit the end of the ring, wrap around to the start (Index 0)
        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

# --- Simulation ---
# 1. Setup Ring with 3 servers, 5 virtual nodes each
servers = ['Server_A', 'Server_B', 'Server_C']
ring = ConsistentHashRing(servers, replicas=5)

# 2. Assign Users
users = ['User_1', 'User_2', 'User_3', 'User_4', 'User_5']
assignments = {}
for u in users:
    assignments[u] = ring.get_node(u)
    print(f"{u} -> {assignments[u]}")

# 3. Scale Out: Add Server_D
print("\n--- Adding Server_D ---\n")
ring.add_node('Server_D')

# 4. Check Re-assignments
moved = 0
for u in users:
    new_node = ring.get_node(u)
    if new_node != assignments[u]:
        print(f"♻️ {u} MOVED: {assignments[u]} -> {new_node}")
        moved += 1
    else:
        print(f"✅ {u} stayed on {new_node}")

print(f"\nTotal Moved: {moved}/{len(users)}")
```

---

## 4. Production Realities (The "Senior" Section)

### A. Cascading Failures
*   **Scenario**: Server A dies. Its load shifts to the *next* server on the ring (Server B).
*   **Risk**: Server B was already at 80% capacity. Now it takes A's load $\rightarrow$ 120% load $\rightarrow$ Server B crashes. Load shifts to C $\rightarrow$ C crashes.
*   **Fix**: **Virtual Nodes** help spread the load of a dead node across *many* other physical nodes, not just one neighbor.

### B. Hot Keys (The "Celebrity" Problem)
*   **Scenario**: Justin Bieber's profile is hosted on Server A. Millions of requests hit Server A. Consistent Hashing doesn't solve this; it balances *keys*, not *traffic*.
*   **Fix**:
    *   **Local Caching**: Cache the hot key on the application servers (L1 Cache).
    *   **Replication**: Store the hot key on multiple nodes (Read Replicas).

### C. Replication Factor (N)
*   Don't just store data on the *first* node found. Store it on the first $N$ unique physical nodes found moving clockwise.
*   *Why?* High Availability. If the primary node dies, the next node already has the data.

---

## 🧠 Flashcards

1.  **Q: Why does Modulo N fail for scaling?**
    *   *A: Changing N changes the denominator for every key, causing massive remapping (Re-hashing storm).*
2.  **Q: How does Consistent Hashing handle "Wrap Around"?**
    *   *A: If a key's hash is higher than the highest server hash, it maps to the first server (index 0) on the ring.*
3.  **Q: What is the main purpose of Virtual Nodes?**
    *   *A: To ensure uniform distribution of keys (prevent data skew) and split the load of a dead node across multiple survivors.*
4.  **Q: Does Consistent Hashing prevent Hot Spots (Hot Keys)?**
    *   *A: No. It balances data volume, not request volume. You need caching or replication for hot keys.*
5.  **Q: What is the typical number of Virtual Nodes per Physical Node?**
    *   *A: Often around 100-200. Higher numbers give better distribution but increase memory usage for the Ring metadata.*
