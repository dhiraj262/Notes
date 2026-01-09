# 🛑 Interview Post-Mortem: "I Bombed Database Sharding"

> **Context**: Sharding is the nuclear option for scaling. It solves write throughput but destroys query flexibility. Candidates often forget that "Joints across shards" are impossible (or extremely slow).

---

## 1. The Trap: "Shard by User ID"

**The Scenario**: You are designing an Order Management System for Amazon.
The interviewer asks: *"The Orders table is too big (10TB). Writes are slow. How do you scale?"*

**The Amateur Answer**: *"I'll shard the database by `User_ID`."*

**The Kill Shot**: *"Okay, efficient for the Buyer. But how does the **Seller** see all their sold items? Or how does the **Warehouse** get a list of all orders to ship today?"*

**The Failure**: You optimized for one access pattern (User View) but broke all others (Seller View, Admin View).
*   To find Seller X's sales, you must query **ALL** 100 shards ("Scatter-Gather") because User A (Shard 1) and User B (Shard 2) could both buy from Seller X.

---

## 2. The Solution: Index Tables (Mapping Tables)

**Concept**: If you shard by `User_ID`, you need a way to look up data by `Order_ID` or `Seller_ID` without querying every shard.

**Strategies**:
1.  **Global Secondary Index (GSI)**: A separate database (or table) that maps `Seller_ID` -> `[User_ID, Order_ID]`.
2.  **Dual Writes**: Write the order to the `User_Shard` (for the buyer) AND the `Seller_Shard` (for the seller).
3.  **Search Service**: Pump all data into Elasticsearch for complex queries (Admin/Warehouse view).

---

## 3. The Implementation: Python Sharding Proxy

**The logic**: A "Router" layer that decides which database node to hit.

```python
import hashlib

class ShardingProxy:
    def __init__(self, num_shards):
        self.num_shards = num_shards
        # Simulating DB Connections
        self.shards = {i: {} for i in range(num_shards)}
        self.global_index = {} # Maps OrderID -> ShardID

    def _get_shard_id(self, user_id):
        # Simple Modulo Sharding
        hash_val = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        return hash_val % self.num_shards

    def insert_order(self, user_id, order_id, data):
        shard_id = self._get_shard_id(user_id)

        print(f"🔄 Routing: User {user_id} -> Shard {shard_id}")

        # 1. Write to Shard
        self.shards[shard_id][order_id] = data

        # 2. Update Global Index (for lookups by OrderID)
        self.global_index[order_id] = shard_id

    def get_order_by_user(self, user_id, order_id):
        # ✅ Direct Access (Efficient)
        shard_id = self._get_shard_id(user_id)
        print(f"🔍 Lookup: User {user_id} -> Shard {shard_id}")
        return self.shards[shard_id].get(order_id)

    def get_order_by_id(self, order_id):
        # ✅ Index Lookup (Efficient)
        shard_id = self.global_index.get(order_id)
        if shard_id is None:
            return None
        print(f"🔍 Lookup: Order {order_id} -> Index says Shard {shard_id}")
        return self.shards[shard_id].get(order_id)

    def get_orders_by_warehouse_scan(self):
        # ❌ Scatter-Gather (Expensive)
        print("💥 SCATTER-GATHER: Querying ALL shards...")
        all_orders = []
        for i in range(self.num_shards):
            print(f"   -> Scanning Shard {i}...")
            all_orders.extend(self.shards[i].values())
        return all_orders

# --- Simulation ---
proxy = ShardingProxy(num_shards=3)

# Insert Orders
proxy.insert_order(user_id="Alice", order_id="ord_1", data="iPhone")
proxy.insert_order(user_id="Bob", order_id="ord_2", data="MacBook")
proxy.insert_order(user_id="Charlie", order_id="ord_3", data="iPad")

# 1. Efficient Query (Shard Key Known)
print(f"Found: {proxy.get_order_by_user('Alice', 'ord_1')}")

# 2. Efficient Query (Index Lookup)
print(f"Found: {proxy.get_order_by_id('ord_2')}")

# 3. Inefficient Query (Warehouse View)
all_items = proxy.get_orders_by_warehouse_scan()
print(f"Total Orders: {len(all_items)}")
```

---

## 4. Production Realities (The "Senior" Section)

### A. Resharding (The Nightmare)
*   **Problem**: You start with 10 shards. You grow to 100TB. You need 20 shards.
*   **Challenge**: Moving data while the system is live.
*   **Fix**: **Hierarchical Sharding** (Directory Based) or Consistent Hashing (Virtual Nodes). Most companies use a "Migration Service" that double-writes to Old and New shards, then switches reads.

### B. Hot Partitions (Celebrity Problem)
*   **Scenario**: Katy Perry (User ID 100) has 100 million followers.
*   **Risk**: If you shard by `User_ID`, the shard containing Katy Perry will melt under read pressure.
*   **Fix**: Isolate celebrities to their own dedicated hardware, or cache aggressively.

### C. Joins are Dead
*   **Fact**: You cannot do `JOIN users ON orders.user_id = users.id` if Users and Orders are on different physical machines.
*   **Fix**: Application-side Joins. Query Users, get IDs. Query Orders with those IDs. Stitch in memory.

---

## 🧠 Flashcards

1.  **Q: What is the "Scatter-Gather" problem?**
    *   *A: When a query doesn't contain the Shard Key, the proxy must send the query to ALL shards and aggregate results. Very slow.*
2.  **Q: How do you handle Multi-Tenant data (SaaS)?**
    *   *A: Shard by `Tenant_ID` (Organization ID). Keeps all data for one company on one shard. Good for isolation.*
3.  **Q: What is a "Mapping Table"?**
    *   *A: A separate table that maps a Non-Shard Key (e.g., Email) to the Shard Key (e.g., User ID) to allow efficient routing.*
4.  **Q: Why avoid Auto-Increment IDs in sharding?**
    *   *A: IDs will collide across shards (Shard A has ID 1, Shard B has ID 1). Use Snowflake IDs (Global Uniqueness).*
