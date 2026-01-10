# ⚖️ System Design Deep Dive: Load Balancers (L4 vs L7)

> **Context**: Understanding traffic distribution layers. Comparing Transport Layer (L4) performance vs Application Layer (L7) intelligence, and handling Session Affinity.

---

## 1. The Trap: "The Magic Black Box"

**The Scenario**: You are designing a Chat App (WebSockets) or a Secure Banking API (HTTPS).
The interviewer asks: *"We have 10 backend servers. How do we distribute traffic?"*
You answer: *"AWS Elastic Load Balancer (ELB)."*

**The Kill Shot**: *"Which type? Network (L4) or Application (L7)? If you use L7, how do you handle the WebSocket persistence? Where does SSL termination happen? What if the LB itself dies?"*

**The Failure**: Treating the LB as a magical router without understanding the **OSI Layers** and **State** implications.

---

## 2. The Solution: L4 vs L7

| Feature | **L4 (Transport Layer)** | **L7 (Application Layer)** |
| :--- | :--- | :--- |
| **Logic** | Routes packets based on IP + Port (TCP/UDP). No inspection of data. | Routes based on URL, Headers, Cookies (HTTP). Inspects content. |
| **Speed** | Extremely Fast (NAT / Packet forwarding). | Slower (Must compute decryption + parsing). |
| **Use Case** | TCP traffic, DNS, extreme throughput, simple routing. | Microservices (API Gateway), A/B Testing, Auth Headers. |
| **Encryption** | Pass-through (Server does decryption). | **SSL Termination** (LB decrypts, re-encrypts or sends plain to backend). |

---

## 3. The Implementation: Weighted Round Robin + Health Checks

**The logic**:
1.  **Weighted RR**: Powerful servers get more requests.
2.  **Health Check**: Background loop pings servers (`/health`). If 404/Timeout, remove from rotation.

```python
import time
import random
import threading

class BackendServer:
    def __init__(self, name, weight=1):
        self.name = name
        self.weight = weight
        self.healthy = True
        self.connections = 0

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers # List of BackendServer objects
        self.lock = threading.Lock()

    def get_server(self):
        with self.lock:
            # 1. Filter Healthy Servers
            healthy_servers = [s for s in self.servers if s.healthy]
            if not healthy_servers:
                return None

            # 2. Weighted Round Robin (Simplified: Selection based on probability)
            # In real RR, we'd keep a counter. Here we use weights for probability.
            total_weight = sum(s.weight for s in healthy_servers)
            pick = random.uniform(0, total_weight)

            current = 0
            for server in healthy_servers:
                current += server.weight
                if pick <= current:
                    server.connections += 1
                    return server
            return healthy_servers[0]

    def health_check_loop(self):
        """Mock: Randomly kill/revive servers"""
        while True:
            time.sleep(2)
            with self.lock:
                # Randomly flip a server's health
                target = random.choice(self.servers)

                # Simulation logic: 10% chance to flip state
                if random.random() < 0.1:
                    target.healthy = not target.healthy
                    status = "🟢 ONLINE" if target.healthy else "🔴 OFFLINE"
                    print(f"[HealthCheck] {target.name} is now {status}")

# --- Simulation ---
s1 = BackendServer("Server_Small", weight=1)
s2 = BackendServer("Server_Big", weight=3) # 3x capacity

lb = LoadBalancer([s1, s2])

# Start Health Check in background
t = threading.Thread(target=lb.health_check_loop, daemon=True)
t.start()

# Simulate Traffic
print("--- Starting Traffic (Press Ctrl+C to stop) ---")
for i in range(10):
    server = lb.get_server()
    if server:
        print(f"Request {i+1} -> {server.name}")
    else:
        print(f"Request {i+1} -> 🚨 503 Service Unavailable")
    time.sleep(0.5)

```

---

## 4. Production Realities (The "Senior" Section)

### A. Sticky Sessions (Session Affinity)
*   **Problem**: User logs in on Server A (Session stored in RAM). Next request goes to Server B (No session). User logged out.
*   **Fix**:
    1.  **L7 Sticky Cookie**: LB injects a cookie `SERVERID=A`. Future requests with this cookie go to A.
    2.  **L4 Source IP Hash**: `hash(ClientIP) % N`. All requests from IP X go to Server A. (Fails if behind a corporate proxy).
    3.  **Real Fix**: **Stateless Backend**. Store session in Redis. Any server can handle any request.

### B. High Availability (LB for the LB)
*   **Problem**: You have 100 web servers behind 1 Nginx LB. Nginx dies. Site down.
*   **Fix**: Active-Passive setup. Two LBs.
    *   **VIP (Virtual IP)**: A floating IP address (e.g., 10.0.0.100).
    *   **Keepalived (VRRP)**: Master owns the VIP. If Master dies, Backup claims the VIP via ARP broadcast.

### C. Connection Draining
*   **Scenario**: You need to upgrade Server A. You just kill it.
*   **Result**: 1000 active users get `502 Bad Gateway`.
*   **Fix**: Enable "Draining". LB stops sending *new* requests to A, but allows *existing* connections to finish (e.g., wait 30s) before killing the node.

---

## 🧠 Flashcards

1.  **Q: What is the main difference between L4 and L7 balancing?**
    *   *A: L4 routes based on IP/Port (No data inspection). L7 routes based on HTTP Headers/URL (Content aware).*
2.  **Q: Why is L7 slower?**
    *   *A: It must establish a TCP connection, perform TLS Handshake, decrypt the request, and parse headers before routing.*
3.  **Q: What is "Hairpinning" (or Loopback)?**
    *   *A: When an internal server tries to access another internal server via the public LB IP, and the router fails to route it back inside.*
4.  **Q: How do you handle HTTPS at the LB level?**
    *   *A: SSL Termination. The LB decrypts the traffic (CPU heavy), inspects it, and sends unencrypted HTTP to the backend (in a trusted VPC).*
5.  **Q: What is "Connection Draining"?**
    *   *A: A process where the LB stops sending new requests to a server but allows existing connections to complete before taking the server offline.*
