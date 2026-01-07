# Day 9: Database Schema Design & Normalization

## 🎯 Goal
Learn how to structure data efficiently. A bad schema kills performance.

---

## 📐 ER Diagrams (Entity-Relationship)
*   **Entity**: A noun (User, Order, Product). Becomes a Table.
*   **Relationship**: How they interact.
    *   **1:1**: User <-> UserProfile.
    *   **1:N**: User <-> Orders. (Foreign Key is in the 'Many' side).
    *   **N:M**: Student <-> Course. (Requires a **Join Table**).

---

## 🧹 Normalization
The process of organizing data to reduce redundancy.

### 1NF (First Normal Form)
*   **Rule**: Atomic values. No repeating groups or arrays in a cell.
*   *Bad*: `[John, "Blue,Red"]` (Two colors in one cell).
*   *Good*: Two rows: `[John, Blue]`, `[John, Red]`.

### 2NF (Second Normal Form)
*   **Rule**: Must be in 1NF + No Partial Dependency.
*   If PK is composite (A, B), non-key attributes must depend on BOTH A and B, not just A.

### 3NF (Third Normal Form)
*   **Rule**: Must be in 2NF + No Transitive Dependency.
*   Non-key attributes should not depend on other non-key attributes.
*   *Bad*: `[ZipCode, City, State]`. City depends on ZipCode, not just the ID.
*   *Good*: Move `ZipCode` logic to a separate `Locations` table.

---

## ⚡ Denormalization
*   **Concept**: Intentionally adding redundancy to improve **Read Performance**.
*   **Why?**: Joins are slow.
*   **Example**: Storing `user_name` in the `comments` table.
    *   *Pros*: Don't need to join `User` table to show a comment section.
    *   *Cons*: If user changes name, you must update millions of comments (Write penalty).

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| **1:N** Relationship: Where does the Foreign Key go? | In the **Many** side table. (e.g., `Orders` table has `user_id`). |
| **N:M** Relationship: How to implement in SQL? | Use a **Join Table** (or Junction Table) containing FKs to both entities (e.g., `StudentCourses` table). |
| What is **ACID**? | Atomicity, Consistency, Isolation, Durability. (Properties of SQL transactions). |
| Why **Denormalize**? | To optimize **Read** performance (avoid joins) at the cost of Write complexity. |

---

## 🛠️ Practical Task
**Task**: Design the Schema for **Instagram**.
1.  **Users**: `id, username, bio`.
2.  **Posts**: `id, user_id, image_url, caption`.
3.  **Follows**: (User A follows User B). `follower_id, followee_id`.
4.  **Likes**: ? (Think about this. Is it N:M?).
5.  **Feed Generation**: If I want to query "All posts from people I follow", write the SQL query.
    *   `SELECT * FROM Posts WHERE user_id IN (SELECT followee_id FROM Follows WHERE follower_id = ME)`.
