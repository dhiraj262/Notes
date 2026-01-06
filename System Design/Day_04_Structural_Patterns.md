# Day 4: Structural Design Patterns

## 🎯 Goal
Understand how to assemble objects and classes into larger structures while keeping them flexible. Structural patterns are all about "Relationships" and "Wrappers".

---

## 🔌 1. Adapter Pattern
> **"If it doesn't fit, use an adapter."**

*   **Concept**: Allows objects with incompatible interfaces to work together. It wraps an existing class with a new interface.
*   **Real-World Analogy**:
    *   **Travel Adapter**: Your US laptop plug (3 pins) doesn't fit into a European socket (2 round pins). You use an adapter. The electricity is the same, but the interface changes.
    *   **Memory Card Reader**: Connects an SD card to a USB port.
*   **Key Idea**: Used when you *cannot* change the existing code (e.g., a 3rd party library) but need it to work with your system.
*   **Code Example**:
    ```java
    // 1. Existing Interface (Incompatible)
    class LegacyPrinter {
        void printOld(String msg) { System.out.println(msg); }
    }

    // 2. Target Interface (What we need)
    interface ModernPrinter {
        void print(String msg);
    }

    // 3. Adapter
    class PrinterAdapter implements ModernPrinter {
        private LegacyPrinter legacy;
        PrinterAdapter(LegacyPrinter legacy) { this.legacy = legacy; }

        @Override
        public void print(String msg) {
            legacy.printOld(msg); // Translating the call
        }
    }
    ```

---

## 🎁 2. Decorator Pattern
> **"Add responsibilities dynamically."**

*   **Concept**: Attach new behaviors to objects by placing these objects inside special wrapper objects that contain the behaviors.
*   **Problem Solved**: **Class Explosion**. Instead of `Pizza`, `PizzaWithCheese`, `PizzaWithCheeseAndHam`, `PizzaWithHam`, you have one `Pizza` and wrappers `CheeseDecorator`, `HamDecorator`.
*   **Real-World Analogy**:
    *   **Coffee Shop**: You start with "Coffee". You wrap it in "Milk". You wrap that in "Sugar". You wrap that in "Whip". The core object is still coffee, but it has layers of extras.
    *   **Winter Jacket**: You wear a shirt. It's cold? You put on a sweater (decorate). Still cold? You put on a coat (decorate). You are still "You", just wrapped.
*   **Code Example**:
    ```java
    interface Coffee { double getCost(); String getDescription(); }

    class SimpleCoffee implements Coffee {
        public double getCost() { return 5.0; }
        public String getDescription() { return "Coffee"; }
    }

    // Abstract Decorator
    abstract class CoffeeDecorator implements Coffee {
        protected Coffee decoratedCoffee;
        public CoffeeDecorator(Coffee c) { this.decoratedCoffee = c; }
        public double getCost() { return decoratedCoffee.getCost(); }
        public String getDescription() { return decoratedCoffee.getDescription(); }
    }

    // Concrete Decorator
    class Milk extends CoffeeDecorator {
        public Milk(Coffee c) { super(c); }
        public double getCost() { return super.getCost() + 1.5; } // Adds cost
        public String getDescription() { return super.getDescription() + ", Milk"; }
    }

    // Usage
    Coffee c = new Milk(new SimpleCoffee()); // Cost: 6.5
    ```

---

## 🎭 3. Facade Pattern
> **"One interface to rule them all."**

*   **Concept**: Provides a simplified interface to a library, a framework, or any other complex set of classes.
*   **Real-World Analogy**:
    *   **Home Theater Remote**: Instead of turning on the TV, then the Sound System, then the Streaming Stick, then setting inputs... you press one button: "Watch Movie". The Remote is the Facade.
    *   **Car Starter**: You turn the key. You don't manually inject fuel, spark the plugs, and crank the engine. The key is the Facade for the Engine subsystem.
*   **Key Difference**: **Adapter** changes the interface to make it compatible. **Facade** makes the interface *simpler*.

---

## 🛡️ 4. Proxy Pattern
> **"The Gatekeeper."**

*   **Concept**: A placeholder for another object to control access to it.
*   **Use Cases**:
    *   **Virtual Proxy**: Lazy loading (e.g., don't load a massive High-Res Image until the user scrolls to it).
    *   **Protection Proxy**: Access control (e.g., only Admins can call `deleteUser()`).
    *   **Remote Proxy**: Representing an object that lives on a different server (RPC).
*   **Real-World Analogy**:
    *   **Credit Card**: It's a proxy for the cash in your bank account.
    *   **Secretary**: You don't talk to the CEO directly. You talk to the secretary (Proxy). If the request is important, they pass it to the CEO.

---

## 🧠 Flashcards (Anki Style)

| Question | Answer |
| :--- | :--- |
| **Adapter** vs **Decorator**: What's the main difference? | **Adapter** converts one interface to another (fixing incompatibility). **Decorator** adds behavior to the interface (enhancing functionality) without changing the interface signature. |
| **Facade** vs **Adapter**: What's the main difference? | **Facade** defines a *new* interface to simplify a complex system. **Adapter** reuses an *existing* interface to make two things work together. |
| **Proxy** vs **Decorator**: What's the main difference? | They look similar (wrappers), but **Proxy** controls access (security, lazy loading), while **Decorator** adds features. |
| Which pattern solves the **"Class Explosion"** problem? | **Decorator Pattern**. |
| Which OOD principle does **Decorator** heavily rely on? | **Open/Closed Principle**. Classes are open for extension (via decorators) but closed for modification. |

---

## 🙋 Interview Questions

1.  **"Design a Vending Machine. Where would you use the State Pattern vs Proxy?"**
    *   *Answer*: State Pattern for internal machine logic (Idle -> HasMoney -> Dispensing). Proxy for the Payment System (communicating with an external Bank API).
2.  **"How does Java IO use the Decorator pattern?"**
    *   *Answer*: `new BufferedReader(new FileReader("file.txt"))`. `BufferedReader` decorates `FileReader` to add buffering capabilities.
3.  **"Implement a Protection Proxy."**
    *   *Task*: Create an interface `Database`, a concrete `RealDatabase`, and a `DatabaseProxy`. The Proxy checks if the user role is "ADMIN" before calling `RealDatabase.delete()`.

---

## 🛠️ Practical Exercise (Day 4 Task)

**Task**: Implement a **Starbucks Order System** using the **Decorator Pattern**.

**Requirements**:
1.  Base Beverage: `Espresso` ($2.00), `Decaf` ($1.50).
2.  Decorators (Condiments):
    *   `Mocha` (Chocolate) (+ $0.20)
    *   `Soy` (+ $0.15)
    *   `Whip` (+ $0.10)
3.  Goal: Allow orders like `Double Mocha Soy Espresso with Whip`.
    *   *Code*: `Beverage b = new Whip(new Soy(new Mocha(new Mocha(new Espresso()))));`
4.  Print the final description and cost.

**Bonus**: Create a `Facade` called `Barista` that has a method `makeTheUsual()` which returns a pre-configured drink.

---

## 📚 Resources
*   [Refactoring Guru: Decorator](https://refactoring.guru/design-patterns/decorator)
*   [Refactoring Guru: Adapter](https://refactoring.guru/design-patterns/adapter)
*   [GeeksForGeeks: Facade vs Adapter vs Proxy](https://www.geeksforgeeks.org/difference-between-adapter-pattern-and-facade-pattern/)
