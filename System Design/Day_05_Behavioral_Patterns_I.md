# Day 5: Behavioral Patterns I (Observer, Strategy, Command)

## 🎯 Goal
Understand how objects communicate and assign responsibilities. Behavioral patterns are about "Communication" and "Algorithms".

---

## 📡 1. Observer Pattern
> **"Don't call us, we'll call you."** (Hollywood Principle)

*   **Concept**: Defines a one-to-many dependency. When one object (Subject) changes state, all its dependents (Observers) are notified automatically.
*   **Real-World Analogy**:
    *   **Newsletter**: You subscribe to a newsletter. When a new issue is out, it's sent to you. You don't call the office every day asking "Is it out yet?".
    *   **Youtube Bell Icon**: The Channel is the Subject. The Subscribers are Observers.
*   **Code**:
    ```java
    interface Observer { void update(String news); }

    class NewsAgency { // Subject
        private List<Observer> subscribers = new ArrayList<>();

        void subscribe(Observer o) { subscribers.add(o); }

        void notify(String news) {
            for(Observer o : subscribers) o.update(news);
        }
    }
    ```

---

## 🗺️ 2. Strategy Pattern
> **"Swap algorithms at runtime."**

*   **Concept**: Define a family of algorithms, encapsulate each one, and make them interchangeable.
*   **Real-World Analogy**:
    *   **Navigation App**: You can choose "Fastest Route", "No Tolls", or "Scenic Route". The destination is the same, but the calculation strategy differs.
    *   **Payment**: Pay via Credit Card, PayPal, or Crypto. All are `pay()`, but the logic is different.
*   **VS State Pattern**: Strategy is about *how* you do something (an algorithm). State is about *what* you are (status).
*   **Code**:
    ```java
    interface RouteStrategy { void buildRoute(String A, String B); }

    class FastestRoute implements RouteStrategy { ... }
    class ScenicRoute implements RouteStrategy { ... }

    class Navigator {
        RouteStrategy strategy;
        void setStrategy(RouteStrategy s) { this.strategy = s; }
        void navigate() { strategy.buildRoute("Home", "Work"); }
    }
    ```

---

## 🤖 3. Command Pattern
> **"Turn a request into an object."**

*   **Concept**: Encapsulate a request as an object, thereby allowing for parameterization of clients with different requests, and the ability to save requests (history/undo).
*   **Real-World Analogy**:
    *   **Diner Order**: You give an order to the waiter. The waiter writes it on a ticket (Command Object). The waiter passes it to the chef. The chef executes it. The waiter doesn't know *how* to cook, just *what* was ordered.
    *   **Smart Home Remote**: Button A turns on Light. Button B opens Garage. Both are "Commands".
*   **Key Feature**: **Undo/Redo**. Since the command is an object, you can store it in a stack and pop it to "undo".

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| **Strategy** vs **State**: Difference? | **Strategy** allows the *client* to choose an algorithm (e.g., sort method). **State** allows the *object* to change behavior when its internal state changes (e.g., Ice -> Water -> Steam). |
| Which pattern enables **Undo/Redo** functionality? | **Command Pattern** (by storing command objects in a stack). |
| In **Observer**, who triggers the update? | The **Subject** (Observable) calls the `update()` method on all registered Observers. |

---

## 🛠️ Practical Task
**Task**: Implement a **Stock Market Notification System**.
1.  `StockMarket` is the Subject.
2.  `MobileApp` and `EmailDashboard` are Observers.
3.  When a stock price changes, notify all observers.
