# Day 23: Testing Strategies

## 🎯 Goal
Code that isn't tested is legacy code the moment it's written.
**Focus**: The Testing Pyramid, TDD, and Mocking.

---

## 🔺 The Testing Pyramid
Shape implies volume. You should have MANY Unit tests, FEWER Integration tests, and VERY FEW E2E tests.

### 1. Unit Tests (Base)
*   **What**: Test a single function/class in isolation.
*   **Dependencies**: Mocked out (DB, API, File System).
*   **Speed**: Milliseconds.
*   **Volume**: 70-80% of tests.
*   **Example**: `calculateTotal(items)` returns correct sum.

### 2. Integration Tests (Middle)
*   **What**: Test how modules work together.
*   **Dependencies**: Real or Dockerized (Test DB).
*   **Speed**: Seconds.
*   **Volume**: 10-20%.
*   **Example**: `UserService` saves User to `Postgres`. `API` endpoint returns 200.

### 3. End-to-End (E2E) Tests (Top)
*   **What**: Test the full flow from user perspective (Browser -> API -> DB).
*   **Tools**: Selenium, Cypress, Playwright.
*   **Speed**: Minutes (Slow, flaky).
*   **Volume**: 1-5% (Critical paths only: Login, Checkout).

---

## 🧪 TDD (Test Driven Development)
**Red -> Green -> Refactor**

1.  **Red**: Write a failing test for a feature that doesn't exist.
2.  **Green**: Write the *minimum* code to pass the test.
3.  **Refactor**: Clean up the code (optimize, deduplicate) while keeping test green.

*   *Benefit*: Forces you to design testable code (Dependency Injection).

---

## 🎭 Mocking vs Stubs

When Unit testing `OrderService`, we don't want to charge a real Credit Card. We use a **Test Double**.

*   **Dummy**: Object passed around but never used (e.g., `null` parameters).
*   **Stub**: Returns fixed data. "When `paymentService.charge()` is called, return `Success`".
*   **Mock**: Verifies behavior. "Assert `paymentService.charge()` was called exactly once with argument `$50`".
*   **Fake**: Working implementation but simpler (e.g., In-Memory HashMap DB instead of SQL).

---

## 📉 Code Coverage
*   **Metric**: % of lines of code executed by tests.
*   **Trap**: High coverage != High quality. You can write tests that assert nothing.
*   **Goal**: High confidence, not just high number. Focus on Branch Coverage (testing `if` AND `else`).

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| **What is Regression Testing?** | Rerunning old tests to ensure new changes didn't break existing functionality. |
| **What is Chaos Engineering?** | Testing resilience by intentionally breaking things in production (e.g., Netflix Chaos Monkey killing servers). |
| **White Box vs Black Box?** | **White Box**: Tester sees code (Unit tests). **Black Box**: Tester only sees inputs/outputs (QA/E2E). |

---

## 🛠️ Practical Task
**Task**: Write a Unit Test for a `RateLimiter`.

```java
class RateLimiter {
    int maxRequests = 5;
    Map<String, Integer> counts = new HashMap<>();

    boolean allow(String userId) {
        int current = counts.getOrDefault(userId, 0);
        if (current >= maxRequests) return false;
        counts.put(userId, current + 1);
        return true;
    }
}
```

**Test Case**:
1.  Call `allow("user1")` 5 times. Assert all return `true`.
2.  Call `allow("user1")` 6th time. Assert returns `false`.
3.  Call `allow("user2")`. Assert returns `true` (Isolation).
