# Day 41: Idempotency

## 🎯 Goal
Understand why doing the same thing twice shouldn't result in double the effect, especially in payments and distributed messaging.
**Focus**: Idempotency Keys, API Design, and implementation strategies.

---

## 🧩 Key Concepts

### 1. Definition
*   **Idempotent Operation**: An operation that can be applied multiple times without changing the result beyond the initial application.
*   *Math*: `f(f(x)) = f(x)`.
*   *Example*: `x = 5` is idempotent. `x = x + 1` is NOT.

### 2. Why is it Critical?
*   **Network Failures**: Client sends "Pay $100". Server charges card but response is lost. Client retries. Without idempotency, user is charged $200.
*   **Message Queues**: "At-least-once" delivery means consumers might receive the same message twice.

### 3. HTTP Methods
*   **GET**: Idempotent (Read-only).
*   **PUT**: Idempotent (Replace resource).
*   **DELETE**: Idempotent (Delete resource; subsequent deletes return 404 but state is same).
*   **POST**: **NOT Idempotent** (Creates new resource every time).

---

## 🛠️ Implementation Strategy: Idempotency Key

1.  **Client** generates a unique ID (UUID) for the request (e.g., `Idempotency-Key: 123`).
2.  **Server** checks a dedicated table/cache:
    *   *If Key exists*: Return the *saved response* immediately. Do not process.
    *   *If Key missing*: Process request, save response + Key, return response.
3.  **Expiry**: Keys are usually stored with a TTL (e.g., 24 hours).

---

## 💻 Code Simulation: Idempotent Payment API

A Python simulation using a dictionary as the storage for keys.

```python
import uuid

# Storage for processed requests: { key: response }
idempotency_store = {}
# Mock Database for balances
balances = {"Alice": 1000}

def process_payment(user, amount, idempotency_key):
    # 1. Check if already processed
    if idempotency_key in idempotency_store:
        print(f"🔄 Replay detected for key {idempotency_key}. Returning cached response.")
        return idempotency_store[idempotency_key]

    # 2. Process logic
    if balances[user] >= amount:
        balances[user] -= amount
        status = "Success"
        print(f"✅ Charged {user} ${amount}. New Balance: {balances[user]}")
    else:
        status = "Insufficient Funds"

    response = {"status": status, "amount": amount}

    # 3. Save result
    idempotency_store[idempotency_key] = response
    return response

# Simulation
key = str(uuid.uuid4())

# First Call (Network failure simulation: Logic runs, but maybe client didn't get ack)
resp1 = process_payment("Alice", 100, key)

# Retry (Client sends exact same request)
resp2 = process_payment("Alice", 100, key)

# Accidental Double Charge (Different Key)
resp3 = process_payment("Alice", 100, str(uuid.uuid4()))
```

---

## ⚠️ The Trap: Race Conditions
*   **Scenario**: Two requests with same Key arrive simultaneously. Both check DB, see "Not Found", and both execute.
*   **The Fix**: **Database Unique Constraint** on `idempotency_key`. The second insert will fail instantly, and the code can catch the error and return the result of the first one (after a short wait).

---

## ⚡ Flashcards
1.  **Where should the Idempotency Key be generated?**
    *   **The Client**. If the server generates it, the purpose is defeated because a retry would generate a new key.
2.  **Is `UPDATE users SET score = 10` idempotent?**
    *   Yes.
3.  **Is `UPDATE users SET score = score + 10` idempotent?**
    *   No.
4.  **What if the request parameters change but the Key is same?**
    *   The server should detect this (hash the params) and reject it as a "Bad Request" or "Conflict", rather than returning the cached response for the old parameters.
