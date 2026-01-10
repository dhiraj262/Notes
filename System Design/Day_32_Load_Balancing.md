# Day 32: Load Balancing - L4 vs L7 & Algorithms

## 🎯 Goal
Understand how to distribute traffic efficiently across multiple servers. The Load Balancer (LB) is the traffic cop of distributed systems.

---

## 🧩 Key Concepts

### 1. The Role of a Load Balancer
*   **Traffic Distribution**: Prevents any single server from being overwhelmed.
*   **High Availability**: Detects unhealthy servers (Health Checks) and stops sending traffic to them.
*   **SSL Termination**: Decrypts HTTPS traffic at the LB, relieving web servers of CPU-intensive encryption work.

### 2. L4 vs L7 Load Balancing

#### Layer 4 (Transport Layer)
*   **What it sees**: IP Addresses and Ports (TCP/UDP).
*   **Data access**: Does **NOT** look at the content of the packet (no HTTP headers, no URL path).
*   **Pros**: Extremely fast, high throughput, simple.
*   **Cons**: Can't route based on content (e.g., can't send `/images` to image-server and `/video` to video-server).
*   **Examples**: AWS Network Load Balancer (NLB), HAProxy (TCP mode).

#### Layer 7 (Application Layer)
*   **What it sees**: HTTP/HTTPS Headers, Cookies, URL Path, Payload.
*   **Data access**: Inspects the actual request data.
*   **Pros**: Smart routing (Microservices support), Sticky Sessions (using cookies), Rate Limiting.
*   **Cons**: Slower (more CPU intensive), higher latency than L4.
*   **Examples**: AWS Application Load Balancer (ALB), Nginx, HAProxy (HTTP mode).

---

## 🧠 LB Algorithms

### 1. Round Robin (Static)
*   **Logic**: Sequential. Request 1 -> Server A, Req 2 -> Server B, Req 3 -> Server A.
*   **Use Case**: When all servers have identical specs and requests are uniform.
*   **Flaw**: Doesn't account for current load or server capacity.

### 2. Weighted Round Robin
*   **Logic**: Assign a "weight" to servers. Server A (Strong) gets 3 requests for every 1 request Server B (Weak) gets.
*   **Use Case**: Heterogeneous environment (some old servers, some new).

### 3. Least Connections (Dynamic)
*   **Logic**: Send request to the server with the fewest active open connections.
*   **Use Case**: Long-lived connections (e.g., WebSockets, File Uploads).

### 4. IP Hash (Sticky)
*   **Logic**: `Hash(Client_IP) % N_Servers`. Ensures a specific user always lands on the same server.
*   **Use Case**: Caching user session data locally on the server (though Redis is preferred).

### 5. Consistent Hashing
*   **Problem**: In normal hashing `Hash(Key) % N`, if N changes (server dies), ALL keys are remapped. Cache misses spike.
*   **Solution**: Map servers and keys to a "Ring" (0 to 2^32). A key goes to the next server on the ring in clockwise direction.
*   **Benefit**: Adding/Removing a node only affects `K/N` keys (neighbors), not all keys.

---

## 💻 Code Simulation: Consistent Hashing

A simplified Python implementation of Consistent Hashing (without Virtual Nodes for brevity).

```python
import hashlib

class ConsistentHash:
    def __init__(self, nodes=None):
        self.nodes = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # Returns a hash integer
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        h = self._hash(node)
        self.nodes.append((h, node))
        self.nodes.sort() # Keep the ring sorted
        print(f"Added {node} at hash {h}")

    def remove_node(self, node):
        h = self._hash(node)
        # Filter out the node
        self.nodes = [n for n in self.nodes if n[1] != node]
        print(f"Removed {node}")

    def get_node(self, key):
        if not self.nodes: return None
        h = self._hash(key)

        # Find the first node clockwise (greater than key hash)
        for node_hash, node_val in self.nodes:
            if node_hash >= h:
                return node_val

        # If we wrapped around, return the first node (Circle)
        return self.nodes[0][1]

# Usage
ch = ConsistentHash(["Server-A", "Server-B", "Server-C"])
print(f"User1 maps to: {ch.get_node('User1')}")
print(f"User2 maps to: {ch.get_node('User2')}")

ch.remove_node("Server-B")
print("--- After removing Server-B ---")
# Only users originally on Server-B should move
print(f"User1 maps to: {ch.get_node('User1')}")
```

---

## 🛠️ Practical Task
**Task**: Set up Nginx as a Load Balancer locally.
1.  Run 2 simple Python HTTP servers on ports 8081 and 8082.
2.  Configure `nginx.conf` upstream block.
3.  Hit `localhost:80` and watch the requests alternate (Round Robin).

**Nginx Config Snippet**:
```nginx
http {
    upstream backend_servers {
        server localhost:8081;
        server localhost:8082;
    }

    server {
        listen 80;
        location / {
            proxy_pass http://backend_servers;
        }
    }
}
```

---

## ⚡ Flashcards
1.  **Why do we need Health Checks?**
    *   To stop sending traffic to dead servers. A "Zombie" server accepting connections but timing out is worse than a hard failure.
2.  **What is the Thundering Herd problem?**
    *   When a large number of processes wake up simultaneously to handle an event, but only one wins, causing a CPU spike. Or when a failed cache causes all requests to hit the DB at once.
3.  **L4 vs L7 for Microservices?**
    *   L7 is usually preferred (e.g., K8s Ingress) because it can route `/api/users` to UserSvc and `/api/orders` to OrderSvc. L4 cannot do this.
