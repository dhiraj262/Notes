# Day 16: Database Indexing

## 🎯 Goal
"My query is slow." The answer is usually Indexes. Understand how they work, the different types, and why you shouldn't just index everything.

---

## 🗂️ How Indexes Work
Imagine a book.
*   **Without Index**: To find "Harry Potter", you read every page (Full Table Scan). O(N).
*   **With Index**: Go to the back, find "H", get page number. O(log N).

### 1. Hash Index
*   **Structure**: A Hash Map in memory. Key -> Disk Address.
*   **Pros**: O(1) Lookups. Extremely fast for exact matches (`WHERE id = 123`).
*   **Cons**:
    *   **No Range Queries**: Cannot do `WHERE age > 18` (Hash is unordered).
    *   **RAM constrained**: Must fit in memory.
*   **Use Case**: Redis, Key-Value stores.

### 2. B-Tree Index (Most Common)
*   **Structure**: Sorted tree.
*   **Pros**:
    *   Good for Exact Match (`=`).
    *   Good for Range Queries (`>`, `<`, `BETWEEN`).
    *   Good for Sorting (`ORDER BY`).
    *   Good for Prefix Search (`LIKE 'Abd%'`).

---

## 🚀 Advanced Indexing Concepts

### Composite Indexes (Multi-Column)
Index on `(Lastname, Firstname)`.
*   **Order Matters**: The index is sorted by Lastname first, then Firstname.
*   **Left-Most Prefix Rule**:
    *   Query `Lastname = 'Bond'` -> **Uses Index**.
    *   Query `Lastname = 'Bond' AND Firstname = 'James'` -> **Uses Index**.
    *   Query `Firstname = 'James'` -> **scans Index (Slow) or ignores it**. The index is useless if you skip the first column.

### Covering Index
An index that contains *all* the columns requested by the query.
*   Query: `SELECT email FROM Users WHERE username = 'john'`.
*   Index: `(username, email)`.
*   **Benefit**: The DB gets the answer directly from the Index structure without visiting the main table (Heap). **Super fast**.

### Index Selectivity
*   **High Selectivity**: Unique values (UUID, Email). Good for indexing.
*   **Low Selectivity**: Few values (Gender, Boolean). Bad for indexing (DB might ignore it because it has to read 50% of rows anyway).

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| What is the **Left-Most Prefix** rule? | In a composite index (A, B), the index helps queries on A, or (A, B), but NOT queries on B alone. |
| Why not index **every column**? | 1. Indexes consume disk space. 2. Every `INSERT/UPDATE/DELETE` becomes slower because all indexes must be updated. |
| What is a **Clustered Index**? | The index *is* the table. The rows are physically stored in the order of the index. Only one per table (usually PK). |
| What is **Index Merge**? | When the DB uses multiple separate indexes for one query (e.g., Index A for condition 1, Index B for condition 2) and intersects the results. Usually slower than a Composite Index. |

---

## 🛠️ Practical Task
**Task**: Optimize a Slow Query.
1.  Assume table `Orders (id, user_id, order_date, status, total)`.
2.  Query: `SELECT * FROM Orders WHERE order_date > '2023-01-01' AND status = 'SHIPPED'`.
3.  **Scenario A**: Index on `order_date`.
4.  **Scenario B**: Index on `status`.
5.  **Scenario C**: Composite Index `(status, order_date)`.
6.  **Analysis**:
    *   Why is C the best? (Hint: Equality first, Range last).
    *   `status` (Equality) reduces the search space. `order_date` (Range) scans the remainder.
