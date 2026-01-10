# 🧮 Deep Dive: Phi Accrual Failure Detection

> **Category**: Failure Detection
> **Core Concept**: Instead of a binary "Up/Down" state, output a **Suspicion Level** ($\Phi$) representing the probability that a node is down.
> **Origin**: Cassandra / Akka.

---

## 1. The Concept

Traditional Heartbeats use a **Fixed Timeout** (e.g., 5s).
*   If network latency spikes to 5.1s $\rightarrow$ False Positive Failure.

**Phi Accrual** is adaptive.
1.  Track the **Inter-Arrival Time** of heartbeats (History).
2.  Calculate Mean ($\mu$) and Deviation ($\sigma$).
3.  When checking, calculate $P(\text{arrival\_time} < t_{now})$.
4.  $\Phi = - \log_{10}(P)$.

### Meaning of Phi ($\Phi$)
*   $\Phi = 1$: 10% chance of mistake (Likely slow).
*   $\Phi = 2$: 1% chance of mistake.
*   $\Phi = 3$: 0.1% chance of mistake.
*   $\Phi = 8$: 0.000001% chance of mistake (Definitely Dead).

---

## 2. Interview Post-Mortem: "The Flapping Cluster"

### 🛑 The Trap
**Scenario**: Cloud Environment (AWS).
**Candidate**: *"I'll set the timeout to 200ms for fast failover."*

**The Kill Shot**: *"AWS network has jitter. Sometimes packets take 300ms. Your system marks nodes dead, rebalances, then marks them up. The cluster is in constant flux (Flapping). How do you handle variable latency?"*

### ✅ The Solution
Use **Phi Accrual**.
*   The system *learns* that 300ms is normal for this network.
*   It only triggers failure if latency hits 1000ms (an outlier based on distribution).

---

## 3. Implementation (Python Logic)

```python
import math

class PhiDetector:
    def __init__(self):
        self.intervals = []

    def add_heartbeat(self, interval_ms):
        self.intervals.append(interval_ms)
        # Keep window small (sliding window)
        if len(self.intervals) > 100:
            self.intervals.pop(0)

    def phi(self, time_since_last_beat_ms):
        if not self.intervals:
            return 0.0

        # Calculate Mean and StdDev
        mean = sum(self.intervals) / len(self.intervals)
        variance = sum((x - mean) ** 2 for x in self.intervals) / len(self.intervals)
        std_dev = math.sqrt(variance) + 0.001 # Avoid div by 0

        # Calculate Probability (Cumulative Distribution Function - CDF)
        # Simplified Normal Distribution logic
        diff = time_since_last_beat_ms - mean
        exponent = -(diff ** 2) / (2 * (std_dev ** 2))
        prob = math.exp(exponent)

        # Phi Formula: -log10(Probability)
        # Handle tiny probabilities
        if prob < 0.0000001: prob = 0.0000001

        return -math.log10(prob)

# --- Test ---
pd = PhiDetector()
# Train with normal latency ~100ms
for _ in range(50): pd.add_heartbeat(100)
for _ in range(50): pd.add_heartbeat(105)

print(f"Delay 110ms -> Phi: {pd.phi(110):.2f} (Low suspicion)")
print(f"Delay 200ms -> Phi: {pd.phi(200):.2f} (High suspicion)")
print(f"Delay 500ms -> Phi: {pd.phi(500):.2f} (Dead)")
```

---

## ⚡ Flashcards
1.  **Q: Why is Phi Accrual better than a static timeout?**
    *   *A: It adapts to network conditions. It works equally well in a fast LAN (low jitter) and a slow WAN (high jitter) without manual tuning.*
2.  **Q: What Phi threshold is typically used?**
    *   *A: Cassandra uses $\Phi=8$ by default.*
3.  **Q: Does it assume a specific distribution?**
    *   *A: Yes, usually Normal (Gaussian) distribution of heartbeat arrival times. (Ideally Exponential, but Normal is good enough approximation).*
