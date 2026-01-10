# Day 35: CAP Theorem & PACELC

## 🎯 Goal
Understand the impossible trinity of distributed systems and the practical trade-offs involved.
**Focus**: Choosing the right database for the job based on business requirements.

---

## 🧩 Key Concepts

### 1. CAP Theorem
In a distributed system, you can only pick **2 out of 3**:
*   **C (Consistency)**: Every read receives the most recent write or an error. (Linearizability).
*   **A (Availability)**: Every request receives a (non-error) response, without the guarantee that it contains the most recent write.
*   **P (Partition Tolerance)**: The system continues to operate despite an arbitrary number of messages being dropped or delayed by the network.

> **Crucial Insight**: In a distributed system (over a network), **P is mandatory**. You cannot choose to have a perfect network.
> Therefore, you effectively have only two choices: **CP** or **AP**.

#### The Choices:
*   **CP (Consistency + Partition Tolerance)**: If the network breaks, stop accepting writes to ensure data doesn't diverge.
    *   *Result*: System returns "Error" or times out.
    *   *Example*: Banking, RDBMS (mostly), MongoDB (default), Redis (Sentinel).
*   **AP (Availability + Partition Tolerance)**: If the network breaks, keep accepting writes on both sides. Deal with the mess (conflicts) later.
    *   *Result*: System returns potentially stale data.
    *   *Example*: Social Media Likes, Cassandra, DynamoDB, Couchbase.

### 2. PACELC Theorem
CAP only explains what happens **during a failure**. What about when the system is running normally?
**PACELC** extends CAP:
*   If **P**artition (Network failure): Choose **A** or **C**.
*   **E**lse (Normal operation): Choose **L**atency or **C**onsistency.

> "Do you want it fast (Latency), or do you want it exactly right immediately (Consistency)?"

*   **DynamoDB/Cassandra**: Prioritize Availability and Low Latency. (AP + EL).
*   **BigTable/HBase**: Prioritize Consistency. (CP + EC).

---

## 🧠 Real World Examples

### Scenario 1: ATM Withdrawal
*   **Requirement**: You cannot withdraw money you don't have.
*   **Choice**: **CP**.
*   **Why**: If the link between the ATM and the Bank is down, the ATM must reject the withdrawal. It cannot guess.

### Scenario 2: Amazon Shopping Cart
*   **Requirement**: Never prevent a user from adding items to cart (Sales > All).
*   **Choice**: **AP**.
*   **Why**: If the network is partition, let the user add the item. If they added "Shoes" on Phone and "Hat" on Laptop during a split, merge them later (Cart = Shoes + Hat).

---

## 💻 Code Simulation: AP vs CP

```python
# Simulating a Network Partition between Node A and Node B

class Node:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode # 'AP' or 'CP'
        self.data = 0
        self.network_active = True

    def write(self, value):
        if not self.network_active:
            if self.mode == 'CP':
                return "Error: Network Down (Consistency Protection)"
            elif self.mode == 'AP':
                self.data = value
                return "Success (Saved Locally - Eventual Consistency)"

        # Normal case
        self.data = value
        return "Success"

    def read(self):
        return self.data

# Setup
node_cp = Node("Bank_Server", "CP")
node_ap = Node("Twitter_Server", "AP")

# Normal Operation
print(f"Normal CP Write: {node_cp.write(100)}")
print(f"Normal AP Write: {node_ap.write(100)}")

# NETWORK FAILURE
node_cp.network_active = False
node_ap.network_active = False
print("\n--- Network Partition Occurs ---")

# CP System (Bank)
print(f"CP Write Attempt: {node_cp.write(200)}")
# Output: Error. We sacrifice Availability to prevent data divergence.

# AP System (Twitter)
print(f"AP Write Attempt: {node_ap.write(200)}")
# Output: Success. We accept the write, risking that other nodes don't know about it yet.
```

---

## ⚡ Flashcards
1.  **Can a system be CA?**
    *   Only if it's not distributed (runs on a single machine). Since networks inevitably fail, CA distributed systems do not exist.
2.  **What is a "Sloppy Quorum"?**
    *   In AP systems (like Cassandra), if the designated replicas are down, the system writes to *any* available node (hinted handoff) to preserve availability.
3.  **Linearizability vs Serializability?**
    *   **Linearizability**: "Recency guarantee" on a single object (CAP Consistency). Read sees the latest write.
    *   **Serializability**: "Isolation guarantee" on transactions (ACID Isolation). Transactions appear to execute in serial order.
