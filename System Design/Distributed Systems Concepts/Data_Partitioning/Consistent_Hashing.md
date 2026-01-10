# 🔄 Deep Dive: Consistent Hashing

> **Category**: Data Partitioning
> **Core Concept**: Distributing keys across $N$ nodes such that adding/removing a node requires minimal data movement ($1/N$).

> **🔗 Related Interview Guide**: [Consistent Hashing Interview Post-Mortem](../../Interview%20Experiences/Consistent_Hashing_Interview_Post_Mortem.md)

---

## 1. The Concept

Consistent Hashing maps both **Data Keys** and **Server Nodes** to a unit circle (Ring) of range $[0, 2^{32}-1]$.
A key is assigned to the **first server** encountered moving clockwise on the ring.

### Key Benefits
*   **Minimal Disruption**: When a node is added, it only "steals" a portion of keys from its clockwise neighbor.
*   **Decentralized**: No central coordinator registry is strictly required (clients can compute destination).

---

## 2. Advanced Concepts (Beyond the Basics)

While the [Interview Guide](../../Interview%20Experiences/Consistent_Hashing_Interview_Post_Mortem.md) covers the basic "Ring + Virtual Nodes" setup, production systems use more sophisticated variants.

### A. Virtual Nodes (VNodes)
*   **Problem**: Non-uniform distribution. If Node A hashes to `0` and Node B hashes to `100`, A owns almost the entire ring.
*   **Solution**: Hash each node $K$ times (e.g., `NodeA-1`, `NodeA-2`...). This interweaves the nodes on the ring, ensuring even load distribution.
*   **Ideal K**: Often 256 for optimal balancing (DynamoDB paper).

### B. Ketama Hashing (Memcached)
*   The standard implementation of Consistent Hashing.
*   Uses MD5 hashing to place points on the ring.
*   Divides the ring into $2^{32}$ points.

### C. Maglev Hashing (Google)
*   **Use Case**: Network Load Balancing (L4).
*   **Difference**: Instead of a Ring, it uses a **Lookup Table** of size $M$ (prime number).
*   **Mechanism**: Each backend generates a permutation of preferences. The table is filled by iterating preferences.
*   **Advantage**: Faster lookup $O(1)$ vs Ring $O(\log N)$, and extremely stable updates.

### D. Bounded Loads (Vimeo)
*   **Problem**: Even with Consistent Hashing, a "Hot Key" or just random variance can overload a specific node.
*   **Solution**: **Bounded Load Consistent Hashing**.
    *   Compute the target node.
    *   Check if `load(node) > c * average_load`.
    *   If yes, skip to the *next* node on the ring.
    *   This limits the max load any server takes (e.g., 1.25x average), preventing "Hot Spot Cascades".

---

## 3. Real World Use Cases
1.  **DynamoDB / Cassandra**: Partitioning data across the cluster.
2.  **Discord**: Routing voice packets to voice servers (Hash Ring).
3.  **Akamai / CDNs**: Mapping URLs to Edge Caches.

---

## ⚡ Flashcards
1.  **Q: What is the complexity of finding a node in a standard Consistent Hash Ring?**
    *   *A: $O(\log N)$ using Binary Search (looking up the sorted hash positions).*
2.  **Q: How does Maglev Hashing improve on Consistent Hashing?**
    *   *A: It provides $O(1)$ lookup using a pre-computed table, but re-computation is expensive ($O(M \log M)$).*
3.  **Q: What happens if the Replication Factor is 3?**
    *   *A: The key is stored on the target node AND the next 2 distinct physical nodes on the ring.*
