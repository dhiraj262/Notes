# Day 1: SOLID Principles

## 🎯 Goal
Master the 5 pillars of Object-Oriented Design. Writing code that adheres to SOLID makes it easier to maintain, test, and extend.

---

## 📖 The Principles

### 1. Single Responsibility Principle (SRP)
> **"A class should have one, and only one, reason to change."**

*   **Concept**: Don't mix responsibilities. If a class handles both business logic and database operations, changing the database schema requires changing the business class. This is bad.
*   **Real-World Analogy**:
    *   **The Swiss Army Knife vs. A Toolset**: A Swiss Army knife does everything but nothing perfectly. A chef's knife is for cutting, a corkscrew is for wine.
    *   **Restaurant Staff**: A waiter takes orders. A chef cooks. A janitor cleans. If the waiter had to cook and clean too, the restaurant would fail during rush hour.
*   **Bad Code**:
    ```java
    class User {
        void register() { /* Logic */ }
        void sendEmail() { /* SMTP Logic */ } // Violation! User class shouldn't know about Email protocols.
        void logError() { /* File IO */ } // Violation!
    }
    ```
*   **Good Code**:
    ```java
    class User { void register() { ... } }
    class EmailService { void sendEmail() { ... } }
    class Logger { void log() { ... } }
    ```

### 2. Open/Closed Principle (OCP)
> **"Software entities should be open for extension, but closed for modification."**

*   **Concept**: You should be able to add new functionality without changing existing source code. Use inheritance or interfaces.
*   **Real-World Analogy**:
    *   **Electric Sockets**: You can plug in a TV, a fridge, or a laptop. You don't need to rewire the house to add a new appliance. The socket is closed for modification but open for extension (via plugs).
*   **Bad Code**:
    ```java
    class PaymentProcessor {
        void process(String type) {
            if (type.equals("Paypal")) { ... }
            else if (type.equals("CreditCard")) { ... } // Modifying class to add new method!
        }
    }
    ```
*   **Good Code**:
    ```java
    interface PaymentMethod { void pay(); }
    class Paypal implements PaymentMethod { ... }
    class CreditCard implements PaymentMethod { ... }

    class PaymentProcessor {
        void process(PaymentMethod method) { method.pay(); } // Works for ANY new method without changing this line.
    }
    ```

### 3. Liskov Substitution Principle (LSP)
> **"Subtypes must be substitutable for their base types."**

*   **Concept**: If class `B` inherits from class `A`, we should be able to pass `B` to any method expecting `A` without breaking functionality.
*   **Real-World Analogy**:
    *   **Duck Test**: If it looks like a duck and quacks like a duck, but needs batteries, you probably have the wrong abstraction.
    *   **Square vs Rectangle**: Mathematically a Square is a Rectangle. But in code, if you set `width` of a Rectangle, `height` doesn't change. If you set `width` of a Square, `height` MUST change. Thus, `Square` cannot be a perfect substitute for `Rectangle` if the behavior differs.
*   **Violation Example**:
    ```java
    class Bird { void fly() {} }
    class Ostrich extends Bird {
        void fly() { throw new Error("Cannot fly"); } // Violation! Ostrich cannot replace Bird safely.
    }
    ```

### 4. Interface Segregation Principle (ISP)
> **"Clients should not be forced to depend on methods they do not use."**

*   **Concept**: Big interfaces are bad. Split them into smaller, specific ones.
*   **Real-World Analogy**:
    *   **USB Ports**: A USB port doesn't require you to connect a mouse, keyboard, and printer all at once to work. It supports specific interactions.
    *   **Restaurant Menu**: You don't hand a customer the employee handbook and the cleaning schedule along with the food menu.
*   **Bad Code**:
    ```java
    interface Worker {
        void work();
        void eat();
    }
    class Robot implements Worker {
        void work() { ... }
        void eat() { throw new Error("Robots don't eat"); } // Forced to implement irrelevant method.
    }
    ```

### 5. Dependency Inversion Principle (DIP)
> **"High-level modules should not depend on low-level modules. Both should depend on abstractions."**

*   **Concept**: Don't hardcode dependencies. Use Interfaces. (This is the core of Dependency Injection).
*   **Real-World Analogy**:
    *   **Lamp and Wall Socket**: You don't solder the lamp directly to the electrical wire in the wall. You use a standard plug (Interface). The lamp depends on the plug shape, not the house wiring.
*   **Bad Code**:
    ```java
    class LightBulb { void turnOn() { ... } }
    class Switch {
        LightBulb bulb = new LightBulb(); // Hard dependency!
        void toggle() { bulb.turnOn(); }
    }
    ```
*   **Good Code**:
    ```java
    interface Switchable { void turnOn(); }
    class LightBulb implements Switchable { ... }
    class Switch {
        Switchable device;
        Switch(Switchable device) { this.device = device; } // Dependency Injected
    }
    ```

---

## 🧠 Flashcards (Anki Style)

| Question | Answer |
| :--- | :--- |
| **S** in SOLID stands for? | **Single Responsibility Principle**: A class should have one reason to change. |
| **O** in SOLID stands for? | **Open/Closed Principle**: Open for extension, closed for modification. |
| **L** in SOLID stands for? | **Liskov Substitution Principle**: Subclasses must be substitutable for base classes. |
| **I** in SOLID stands for? | **Interface Segregation Principle**: Many specific interfaces are better than one general-purpose interface. |
| **D** in SOLID stands for? | **Dependency Inversion Principle**: Depend on abstractions, not concretions. |
| Why is SRP important? | It reduces coupling. If a class does too much, changing one thing might break unrelated features. |
| How do you fix an LSP violation? | Use composition instead of inheritance, or ensure the superclass is abstract enough. |

---

## 🙋 Interview Questions

1.  **"Explain a time you refactored code to follow SOLID."**
    *   *Tip*: Talk about breaking a massive "God Class" (e.g., `OrderManager` handling DB, Email, and Logic) into `OrderRepository`, `NotificationService`, and `OrderService`.
2.  **"Is Singleton pattern a violation of SRP?"**
    *   *Answer*: Debatable. It controls its own creation (responsibility 1) and performs its business logic (responsibility 2). Many consider it an anti-pattern for this reason (and testing difficulty).
3.  **"How does Dependency Injection relate to DIP?"**
    *   *Answer*: DI is a technique/pattern to *implement* the Dependency Inversion Principle.
4.  **"Design a Parking Lot. Where would you use OCP?"**
    *   *Answer*: Pricing Strategy. I would make `CalculationStrategy` an interface. Today we charge by hour (`HourlyStrategy`), tomorrow we might charge by demand (`DynamicStrategy`). The `ParkingLot` class won't change, we just pass a new strategy.

---

## 🛠️ Practical Exercise (Day 1 Task)

**Task**: Refactor this "Bad" Code.
1.  Identify which principles are broken.
2.  Rewrite it to follow SOLID.

```java
public class ReportManager {
    public void generateReport(String type) {
        if (type.equals("PDF")) {
            System.out.println("Generating PDF...");
        } else if (type.equals("HTML")) {
            System.out.println("Generating HTML...");
        }
    }

    public void saveToFile(String filename) {
        // Logic to write to disk
    }

    public void emailReport(String email) {
        // Logic to send SMTP
    }
}
```

*Solution Hint*: Break into `ReportGenerator` (Interface), `PDFGenerator`, `HTMLGenerator`, `ReportSaver`, and `EmailSender`.

---

## 📚 Resources
*   [DigitalOcean: SOLID Principles in Java](https://www.digitalocean.com/community/conceptual/solid-principles-in-software-architecture)
*   [GeeksForGeeks: SOLID Principles](https://www.geeksforgeeks.org/solid-principle-in-programming-understand-with-real-life-examples/)
*   [Refactoring Guru: Design Patterns](https://refactoring.guru/)
