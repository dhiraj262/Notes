# Day 24: Code Quality

## 🎯 Goal
Write code that humans can understand, maintain, and extend.
**Focus**: Clean Code principles, Refactoring, and Code Reviews.

---

## 🧼 Core Principles

### 1. DRY (Don't Repeat Yourself)
*   **Rule**: Every piece of knowledge must have a single, unambiguous representation.
*   **Violation**: Copy-pasting validation logic in `Login` and `Signup`.
*   **Fix**: Extract to `Validator` class.

### 2. KISS (Keep It Simple, Stupid)
*   **Rule**: Most systems work best if they are kept simple rather than made complicated.
*   **Violation**: Using a complex Design Pattern (Factory) when a simple `if` statement suffices.

### 3. YAGNI (You Aren't Gonna Need It)
*   **Rule**: Don't build features for "future use cases" that don't exist yet.
*   **Violation**: Adding a "Plugin System" for a calculator app that only adds 2 numbers.

### 4. SOLID
(Recap from Day 1) - Single Responsibility is the most important for readability.

---

## 🧹 Refactoring
Refactoring is changing the *structure* of code without changing its *behavior*.

### Common Smells
1.  **Long Method**: If it doesn't fit on a screen, split it.
2.  **Large Class**: "God Object" doing everything. Split it.
3.  **Magic Numbers**: `if (status == 2)`. Use `if (status == Status.PAID)`.
4.  **Feature Envy**: Class A accesses fields of Class B more than its own. Move the logic to Class B.

---

## 📝 Code Review Checklist
When reviewing a PR (Pull Request), look for:

### Functional
*   [ ] Does the code do what the ticket says?
*   [ ] Are edge cases handled? (Nulls, Empty lists, Negatives).
*   [ ] Are there tests? Do they pass?

### Readability
*   [ ] Variable naming: `d` vs `daysSinceLogin`.
*   [ ] Comments: Explain "Why", not "What". Code explains "What".

### Security & Performance
*   [ ] SQL Injection? (Parametrized queries used?)
*   [ ] N+1 Queries? (Looping over DB calls).
*   [ ] Thread Safety? (Shared mutable state).

---

## 📉 Technical Debt
*   **Definition**: The implied cost of additional rework caused by choosing an easy solution now instead of using a better approach that would take longer.
*   **Management**: Debt is okay (like financial debt) if you pay it back (Refactor). If you ignore it, interest (bugs, slow dev speed) compounds.

---

## 🛠️ Practical Task
**Task**: Refactor this "Bad Code".

```java
public void process(Order o) {
    if (o.total > 100) {
        o.total = o.total * 0.9; // Magic Number
    }
    // ... 50 lines of shipping logic
    // ... 50 lines of email logic
}
```

**Refactored**:
```java
public void processOrder(Order order) {
    applyDiscount(order);
    shipOrder(order);
    sendConfirmation(order);
}

private void applyDiscount(Order order) {
    final double DISCOUNT_THRESHOLD = 100.0;
    final double DISCOUNT_RATE = 0.9;

    if (order.getTotal() > DISCOUNT_THRESHOLD) {
        order.applyDiscount(DISCOUNT_RATE);
    }
}
```
