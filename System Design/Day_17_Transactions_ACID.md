# Day 17: Transactions (ACID)

## 🎯 Goal
Understand the promises a database makes. When you send money, you want to be sure it arrives. ACID is the contract.

---

## 🧪 ACID Properties

### 1. Atomicity (All or Nothing)
*   A transaction is a single unit of work.
*   If any step fails, the **entire** transaction is rolled back.
*   **Implementation**: Write-Ahead Log (WAL). Undo logs.

### 2. Consistency (Rules)
*   The database moves from one valid state to another valid state.
*   Adheres to constraints (Foreign Keys, Unique, Not Null).
*   **Note**: "Consistency" in CAP theorem is different (see Distributed Systems).

### 3. Isolation (Independence)
*   Concurrent transactions should not interfere with each other.
*   This is the most complex part. (See Isolation Levels below).
*   **Implementation**: Locks (Pessimistic) or MVCC (Optimistic).

### 4. Durability (Persistence)
*   Once a transaction is committed, it remains committed even if the power goes out.
*   **Implementation**: Flush to disk (WAL) before confirming success.

---

## 🕵️ Isolation Levels
Trade-off between **Data Integrity** and **Performance**.

### Read Phenomena (The Bugs)
1.  **Dirty Read**: Reading uncommitted data from another transaction. (Bad!)
2.  **Non-Repeatable Read**: Reading the same row twice gets different data (someone updated it).
3.  **Phantom Read**: Running the same range query twice gets different set of rows (someone inserted a new row).

### The Levels (Weakest to Strongest)
1.  **Read Uncommitted**: Dirty Reads allowed. Fastest. (Rarely used).
2.  **Read Committed** (Default in PostgreSQL/Oracle): No Dirty Reads. Non-Repeatable reads possible.
3.  **Repeatable Read** (Default in MySQL): No Dirty/Non-Repeatable reads. Phantoms possible (mostly prevented in MySQL via Gap Locks).
4.  **Serializable**: Strict execution. No concurrency anomalies. Slowest. Use for financial ledgers.

---

## 🛡️ MVCC (Multi-Version Concurrency Control)
How do modern DBs allow Readers to read without blocking Writers?
*   **Concept**: Keep multiple versions of a row.
*   **Mechanism**:
    *   Writer creates a new version of the row (V2).
    *   Reader (Transaction A) sees snapshot V1.
    *   Reader (Transaction B) sees snapshot V2.
*   **Benefit**: **Readers don't block Writers. Writers don't block Readers.**

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| What is a **Dirty Read**? | Reading data that has been written by another transaction but not yet committed. |
| Which Isolation Level prevents **Dirty Reads**? | Read Committed (and above). |
| What does **MVCC** achieve? | It allows non-blocking reads. A reader sees a consistent snapshot of the DB at the start of the transaction. |
| Difference between **Pessimistic** and **Optimistic** Locking? | Pessimistic locks the row immediately (assume conflict). Optimistic checks version at commit time (assume no conflict). |

---

## 🛠️ Practical Task
**Task**: Simulate Transaction Anomalies (Mental or SQL).
1.  **Scenario**: "Lost Update".
    *   Row `count = 10`.
    *   Tx1 reads 10.
    *   Tx2 reads 10.
    *   Tx1 writes 11 (commit).
    *   Tx2 writes 11 (commit).
    *   Result: 11. Should be 12.
2.  **Fix**:
    *   **Pessimistic**: `SELECT ... FOR UPDATE` (Locks the row).
    *   **Optimistic**: `UPDATE table SET count = 11 WHERE id = 1 AND count = 10` (Check condition).
