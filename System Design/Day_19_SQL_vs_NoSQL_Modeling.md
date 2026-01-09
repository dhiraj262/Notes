# Day 19: SQL vs NoSQL Modeling

## 🎯 Goal
The hardest part of NoSQL isn't installing it; it's **Modeling**. You have to unlearn "Normalization".

---

## 🔄 Paradigm Shift

### SQL: Normalized (Write Optimization)
*   **Goal**: Reduce redundancy.
*   **Method**: Split data into `Users`, `Orders`, `Products`.
*   **Query**: JOIN them at read time.
*   **Pro**: Update once, reflected everywhere.
*   **Con**: Reads are slow (Joins).

### NoSQL: Denormalized (Read Optimization)
*   **Goal**: Fast Reads.
*   **Method**: Store data **together** in the shape it will be queried.
*   **Query**: `get(key)`. No Joins.
*   **Pro**: Blazing fast reads. Scalable (easy to shard).
*   **Con**: Complex Updates. (If user changes name, update 1000 orders).

---

## 🎨 Modeling Patterns

### 1. Embedding (Document Store)
Instead of a separate `Address` table, put the address *inside* the User document.
*   **Use when**: 1:1 or 1:Few relationship. Data is viewed together.
```json
{
  "id": 1,
  "name": "Jules",
  "addresses": [
    { "city": "NYC", "zip": "10001" }
  ]
}
```

### 2. Referencing (Document Store)
Store the ID, like a Foreign Key.
*   **Use when**: 1:Many (unbounded) or Many:Many. Data is updated frequently.
```json
// User Doc
{ "id": 1, "name": "Jules" }
// Order Doc
{ "id": 99, "user_id": 1, "total": 50 }
```
*   **Trade-off**: Requires 2 queries (Application-side Join).

### 3. Bucketing (Cassandra/Time Series)
Group related data into a single row to optimize fetching.
*   **Scenario**: IoT Sensor readings every second.
*   **Naive**: 1 row per second (Too many rows).
*   **Bucketed**: 1 row per minute (contains 60 readings in columns).

---

## ⚔️ The Duel: When to use what?

| Criterion | SQL (RDBMS) | NoSQL |
| :--- | :--- | :--- |
| **Data Structure** | Structured, Relational | Unstructured, Hierarchical |
| **Consistency** | Strong (ACID) | Eventual (BASE) - mostly |
| **Scaling** | Vertical (Bigger machine) | Horizontal (More machines) |
| **Query Pattern** | Ad-hoc, Analytics | Known access patterns |

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| What is the **N+1 Problem**? | Fetching a list of N items, then performing 1 additional query for *each* item (N queries). Total N+1. Bad for performance. |
| What is **Polyglot Persistence**? | Using different databases for different needs within the same microservices architecture (e.g., SQL for Orders, Redis for Session, Elastic for Search). |
| Why is **Sharding** easier in NoSQL? | Data is often aggregate-oriented (self-contained documents/rows) and doesn't require cross-shard JOINs. |

---

## 🛠️ Practical Task
**Task**: Model a **Blog System**.
1.  **Entities**: Users, Posts, Comments.
2.  **SQL Approach**: 3 Tables. Foreign Keys.
3.  **MongoDB Approach**:
    *   **User**: Separate Collection.
    *   **Post**: Collection.
    *   **Comments**: **Embed** the first 10 comments in the Post document (for speed). **Reference** the rest in a separate Comments collection (if infinite).
    *   *Why?* Most users only read the top comments.
