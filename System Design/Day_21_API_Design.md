# Day 21: API Design

## 🎯 Goal
Understand how to design clean, scalable, and intuitive APIs.
**Focus**: REST vs GraphQL, Resource Naming, and Best Practices.

---

## 🌐 REST (Representational State Transfer)
The standard for web APIs. Based on resources.

### 1. Resources (Nouns)
*   **Good**: `/users`, `/orders/123/items`
*   **Bad**: `/getUsers`, `/createOrder` (Verbs in URL are RPC style, not REST).

### 2. HTTP Verbs (Actions)
*   **GET**: Retrieve. Safe & Idempotent. (`GET /users/1`)
*   **POST**: Create. Not Idempotent. (`POST /users`)
*   **PUT**: Replace. Idempotent. (`PUT /users/1`)
*   **PATCH**: Partial Update. (`PATCH /users/1` - only update email)
*   **DELETE**: Remove. Idempotent.

### 3. Status Codes
*   **2xx (Success)**: 200 OK, 201 Created, 204 No Content.
*   **3xx (Redirection)**: 301 Moved Permanently, 304 Not Modified (Caching).
*   **4xx (Client Error)**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found.
*   **5xx (Server Error)**: 500 Internal Error, 502 Bad Gateway.

### 4. Versioning
Always version your API.
*   **URL**: `/v1/users` (Most common).
*   **Header**: `Accept: application/vnd.myapi.v1+json`.

---

## ⚛️ GraphQL
A query language for APIs. Solves "Over-fetching" and "Under-fetching".

### The Problem with REST
*   **Over-fetching**: You want just user's name, but `GET /users/1` returns address, history, etc.
*   **Under-fetching**: You want User + their Last Order. REST requires 2 calls: `GET /users/1` then `GET /orders?user_id=1`.

### The GraphQL Solution
One Endpoint (`POST /graphql`). Client asks exactly what it needs.

```graphql
query {
  user(id: "1") {
    name
    lastOrder {
      total
      items { name }
    }
  }
}
```

### Pros vs Cons
*   **Pros**: Flexible, Typed Schema, ONE network call.
*   **Cons**: Complexity, Caching is harder (everything is POST 200 OK), N+1 Query problem.

---

## 🛡️ API Security & Best Practices

### 1. Pagination
Never return all rows.
*   **Offset/Limit**: `/users?offset=100&limit=20` (Slow for large offsets).
*   **Cursor-based**: `/users?cursor=xyz` (Better for infinite scroll).

### 2. Rate Limiting
Protect your service.
*   Return `429 Too Many Requests`.
*   Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`.

### 3. Idempotency Keys
For payments (`POST /charge`). Client sends `Idempotency-Key: UUID`. If request times out, retrying with same Key ensures we don't charge twice.

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| **PUT vs PATCH**? | PUT replaces the *entire* resource. PATCH updates only specified fields. |
| **Why is POST not idempotent?** | Calling POST twice creates *two* resources. Calling PUT twice results in the *same* state as calling it once. |
| **What is HATEOAS?** | Hypermedia As The Engine Of Application State. API returns links to next actions (e.g., `links: { "next": "/page/2" }`). |

---

## 🛠️ Practical Task
**Task**: Design a REST API for a **Todo App**.
1.  List Todos: `GET /todos` (Support filtering `?completed=true`).
2.  Create Todo: `POST /todos` (Body: `{ "text": "Buy milk" }`).
3.  Mark Complete: `PATCH /todos/{id}` (Body: `{ "completed": true }`).
4.  Delete: `DELETE /todos/{id}`.

**Question**: How would you design the API to **bulk delete** completed todos?
*   *Option A*: `DELETE /todos` (dangerous).
*   *Option B*: `POST /todos/delete-completed` (RPC style).
*   *Option C*: `DELETE /todos?completed=true` (RESTful).
