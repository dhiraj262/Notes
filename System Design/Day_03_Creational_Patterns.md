# Day 3: Creational Design Patterns

## 🎯 Goal
Understand how to create objects flexibly and cleanly. "New is Glue" — using the `new` keyword everywhere tightly couples your code. Creational patterns solve this.

---

## 🏗️ 1. Singleton Pattern
> **"There can be only one."**

*   **Concept**: Ensure a class has only one instance and provide a global point of access to it.
*   **Real-World Analogy**:
    *   **The Government**: A country has only one official government. No matter who asks (a citizen, a corporation), they all interact with the same government instance.
    *   **Printer Spooler**: If ten programs want to print, you don't want ten printer managers sending data simultaneously. You want one manager queueing requests.
*   **Thread Safety (The Tricky Part)**:
    *   **Naive Implementation**: Fails in multi-threaded environments (race conditions).
    *   **Double-Checked Locking**: The industry standard for lazy loading.

### Code Example (Java - Thread Safe)
```java
class Database {
    // Volatile ensures changes are visible to other threads immediately
    private static volatile Database instance;

    private Database() {
        // Private constructor prevents "new Database()" from outside
    }

    public static Database getInstance() {
        if (instance == null) { // First check (Performance)
            synchronized (Database.class) {
                if (instance == null) { // Second check (Safety)
                    instance = new Database();
                }
            }
        }
        return instance;
    }
}
```

---

## 🏭 2. Factory Method Pattern
> **"Let subclasses decide which class to instantiate."**

*   **Concept**: Define an interface for creating an object, but let subclasses alter the type of objects that will be created.
*   **Real-World Analogy**:
    *   **Logistics Company**: A logistics company delivers products. Originally, they only used Trucks. Now they add Ships. The "Plan Delivery" process is the same, but the "Create Vehicle" step differs (Truck vs Ship).
*   **Bad Code**:
    ```java
    void deliver(String type) {
        if (type.equals("Road")) new Truck().deliver();
        else if (type.equals("Sea")) new Ship().deliver(); // Modification required for Air!
    }
    ```
*   **Good Code**:
    ```java
    abstract class Logistics {
        // The "Factory Method"
        abstract Transport createTransport();

        void planDelivery() {
            Transport t = createTransport(); // I don't know WHAT 't' is, only that it moves.
            t.deliver();
        }
    }
    ```

---

## 🧱 3. Builder Pattern
> **"Construct complex objects step by step."**

*   **Concept**: Separate the construction of a complex object from its representation.
*   **Problem Solved**: **Telescoping Constructor Problem**.
    *   `new User("John", "Doe", null, null, true, false, 1990...)` -> What are those nulls? What is true?
*   **Real-World Analogy**:
    *   **Subway / Chipotle**: You don't order a "SandwichType4". You say: "Start with Italian bread. Add turkey. Add cheese. Skip onions. Add mayo." You build the object step-by-step.
*   **Code Example**:
    ```java
    User user = new User.UserBuilder()
        .setFirstName("John")
        .setLastName("Doe")
        .setAge(30) // Optional
        .build();
    ```

---

## 🧠 Flashcards (Anki Style)

| Question | Answer |
| :--- | :--- |
| What is the **Telescoping Constructor** problem? | When a class has many constructors with increasing numbers of parameters, making it hard to read and maintain. Solved by **Builder Pattern**. |
| Why is the **Singleton** pattern considered an anti-pattern by some? | It introduces global state, making unit testing difficult (mocking is hard) and hiding dependencies. |
| What is the difference between **Factory Method** and **Abstract Factory**? | Factory Method creates *one* product (e.g., "Create Chair"). Abstract Factory creates *families* of related products (e.g., "Create Chair AND Table AND Sofa" for Victorian style). |
| What keyword ensures variable visibility across threads in Java Singleton? | `volatile`. |

---

## 🙋 Interview Questions

1.  **"How would you break a Singleton pattern?"**
    *   *Answer*: Reflection (can access private constructors) or Serialization/Deserialization (creates a new instance unless `readResolve` is implemented).
2.  **"When should you use Builder instead of Factory?"**
    *   *Answer*: Use **Factory** when you need to create one of several polymorphic classes (Subclassing). Use **Builder** when you are creating a single complex object with many optional parameters/configurations.
3.  **"Implement a Singleton in Python/C++."**
    *   *Tip*: Know the language-specifics. (Python uses `__new__` or a decorator).

---

## 🛠️ Practical Exercise (Day 3 Task)

**Task**: Implement a **Logger** system using Singleton (so all logs go to one file) and a **Pizza Ordering System** using Builder.

**Pizza Builder Requirements**:
1.  Mandatory: Size (Small, Medium, Large).
2.  Optional: Cheese, Pepperoni, Mushrooms, Bacon.
3.  Usage: `Pizza p = new Pizza.Builder(Size.LARGE).addCheese().addBacon().build();`

**Bonus**: Make the Logger thread-safe.

---

## 📚 Resources
*   [Refactoring Guru: Singleton](https://refactoring.guru/design-patterns/singleton)
*   [Refactoring Guru: Builder](https://refactoring.guru/design-patterns/builder)
*   [Baeldung: Java Singleton](https://www.baeldung.com/java-singleton)
