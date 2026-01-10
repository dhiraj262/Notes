# 💓 Deep Dive: Heartbeat

> **Category**: Failure Detection
> **Core Concept**: A periodic signal sent by a node to indicate "I am alive". Absence of signal = Failure.

---

## 1. The Concept

In a cluster, how do you know if a node is dead? You can't distinguish between:
1.  Node Crashed.
2.  Network Packet Dropped.
3.  Node Process Slow (GC Pause).

**Heartbeating** is the standard mechanism.
*   **Push**: Node A sends "Ping" to Node B every 1s.
*   **Pull**: Node B asks "Are you there?" every 1s.

---

## 2. Implementation (Python Simulation)

```python
import time
import threading

class Monitor:
    def __init__(self, timeout=3):
        self.last_beat = time.time()
        self.timeout = timeout
        self.running = True

    def receive_heartbeat(self):
        self.last_beat = time.time()
        print("💓 Thump-Thump")

    def check_loop(self):
        while self.running:
            time.sleep(1)
            age = time.time() - self.last_beat
            if age > self.timeout:
                print(f"💀 FAILURE DETECTED! Last beat {age:.1f}s ago")
                self.running = False
            else:
                print(f"✅ OK (Age: {age:.1f}s)")

# --- Test ---
mon = Monitor(timeout=2.5)

# Start Monitor
t = threading.Thread(target=mon.check_loop)
t.start()

# Simulate Heartbeats
mon.receive_heartbeat()
time.sleep(1)
mon.receive_heartbeat()
time.sleep(1)
mon.receive_heartbeat()

# Simulate Crash (Stop sending)
print("--- Node Crash ---")
t.join() # Wait for monitor to detect failure
```

---

## 3. Production Realities

### A. The Timeout Dilemma
*   **Timeout too short (1s)**: False Positives. A small network blip marks a healthy node as dead. Cluster rebalances unnecessarily (Storm).
*   **Timeout too long (60s)**: Slow Failover. Users see errors for 60s before the system fixes itself.

### B. Adaptive Heartbeats
*   Instead of a fixed `3s` timeout, measure the *distribution* of arrival times.
*   If heartbeats usually arrive in 100ms $\pm$ 10ms, and we wait 500ms, it's dead.
*   (See **Phi Accrual Failure Detection**).

### C. Hierarchical Heartbeats
*   In massive clusters (10k nodes), N-to-N heartbeating is $O(N^2)$ traffic.
*   **Solution**: Gossip Protocol (Random subset) or Hierarchy (Rack Leader checks Rack Members).

---

## ⚡ Flashcards
1.  **Q: What is the difference between Push and Pull heartbeats?**
    *   *A: Push is standard (I tell you I'm alive). Pull is used when the central monitor is behind a firewall or NAT.*
2.  **Q: Why are False Positives dangerous?**
    *   *A: They trigger "Flapping". Node marked dead -> Rebalance data -> Node comes back -> Rebalance data. This kills performance.*
3.  **Q: Does a Heartbeat prove the app is working?**
    *   *A: No. It only proves the OS/Network is working. The app thread could be deadlocked. (Need Application-Level Health Checks).*
