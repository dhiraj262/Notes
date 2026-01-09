# Day 18: NoSQL Types

## 🎯 Goal
"NoSQL" isn't one thing. It's a family of 4 distinct database types. Know when to use which.

---

## 1. Key-Value Stores
*   **Data Model**: Hash Map. `Key -> Blob`.
*   **Behavior**:
    *   O(1) Reads/Writes.
    *   Values are opaque (DB doesn't know what's inside).
*   **Use Cases**: Caching (Redis), Session Management, Shopping Cart.
*   **Examples**: Redis, Memcached, DynamoDB.

## 2. Document Stores
*   **Data Model**: JSON/BSON documents. `Key -> JSON`.
*   **Behavior**:
    *   Flexible Schema (schemaless).
    *   Can index fields *inside* the document.
*   **Use Cases**: Content Management (CMS), Catalogs, User Profiles.
*   **Examples**: MongoDB, Couchbase.

## 3. Column-Family Stores (Wide-Column)
*   **Data Model**: 2D Map. `Row Key -> (Column Family: Column Key -> Value)`.
*   **Behavior**:
    *   Optimized for **Writing**. (Uses LSM Trees).
    *   Great for Time-series data.
*   **Use Cases**: Metrics, IoT sensor data, Chat History (write heavy).
*   **Examples**: Cassandra, HBase, ScyllaDB.

## 4. Graph Databases
*   **Data Model**: Nodes and Edges.
*   **Behavior**:
    *   Optimized for **Relationships**.
    *   "Index-free adjacency" (Traversing neighbors is O(1) per pointer).
*   **Use Cases**: Social Networks, Fraud Detection (rings), Recommendation Engines.
*   **Examples**: Neo4j, Amazon Neptune.

---

## ⚖️ Comparison

| Type | Best For | Weakness | Query Pattern |
| :--- | :--- | :--- | :--- |
| **Key-Value** | Speed, Simplicity | No complex queries | `get(k)`, `put(k,v)` |
| **Document** | Flexibility, Dev Speed | Joins are hard/slow | `find({ "age": { "$gt": 18 } })` |
| **Column** | Massive Writes, Big Data | rigid schema design | Query by Partition Key |
| **Graph** | Deep connections | Scaling (Hard to shard) | `MATCH (a)-[:KNOWS]->(b)` |

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| Which NoSQL type is best for a **Social Graph** (Friends of Friends)? | Graph Database (Neo4j). |
| Which NoSQL type is best for **High Speed Caching**? | Key-Value Store (Redis). |
| Why is **Cassandra** good for writes? | It uses LSM Trees (Append-only logs) and avoids random I/O. |
| What is "Schemaless"? | The database doesn't enforce the structure. Each row/document can have different fields. |

---

## 🛠️ Practical Task
**Task**: Choose the DB for these features.
1.  **Storing User Sessions** (Expires in 30m). -> ? (Redis)
2.  **Product Catalog** (Different attributes for Clothes vs Electronics). -> ? (MongoDB)
3.  **Chat Messages** (Billions of writes, query by GroupID + Time). -> ? (Cassandra)
4.  **Bank Ledger**. -> ? (PostgreSQL - Stick to SQL/ACID for money!)
