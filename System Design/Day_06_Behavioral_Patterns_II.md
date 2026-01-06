# Day 6: Behavioral Patterns II (State, Template, Chain of Responsibility)

## 🎯 Goal
Master patterns that manage complex control flows and state-dependent behavior. These patterns are essential for building robust engines (e.g., Workflow Engines, Game Engines, Security Filters).

---

## 🚦 1. State Pattern
> **"I act differently depending on my mood."**

### Concept
Allows an object to alter its behavior when its internal state changes. The object will appear to change its class.
*   **Without State Pattern**: You have a class full of `if (state == A) ... else if (state == B)`. This is hard to maintain.
*   **With State Pattern**: Each state is a separate class. The Context delegates the call to the current State object.

### Deep Dive: State vs Strategy
This is a common interview confusion.
*   **Strategy Pattern**: The **Client** chooses the algorithm. "I want to go to the airport using *UberStrategy*". The goal is the same, the method differs. Strategies are usually independent.
*   **State Pattern**: The **Context** (or the State itself) changes the state. "I am in *LoadingState*, now I switch to *PlayState*". The client doesn't explicitly choose "PlayState", it happens due to an event.

### Real-World Analogy
*   **Vending Machine**:
    *   State: `Idle`. Action: Insert Coin -> Transition to `HasMoney`.
    *   State: `HasMoney`. Action: Eject Coin -> Transition to `Idle`.
    *   State: `HasMoney`. Action: Select Item -> Transition to `Dispensing`.
*   **TCP Connection**: `Established`, `Listening`, `Closed`. The `send()` method behaves differently in each state (sends data vs throws error).

### Code Lab (Refactoring)
**Before (Bad Code - The "Switch" Smell)**:
```java
class AudioPlayer {
    String state = "STOPPED";

    void pressPlay() {
        if (state.equals("STOPPED")) {
            System.out.println("Playing song...");
            state = "PLAYING";
        } else if (state.equals("PLAYING")) {
            System.out.println("Pausing...");
            state = "PAUSED";
        } else if (state.equals("PAUSED")) {
            System.out.println("Resuming...");
            state = "PLAYING";
        }
    }
}
```

**After (Good Code - State Pattern)**:
```java
// 1. Interface
interface State {
    void pressPlay(AudioPlayer player);
}

// 2. Concrete States
class StoppedState implements State {
    public void pressPlay(AudioPlayer player) {
        System.out.println("Playing song...");
        player.setState(new PlayingState()); // Transition
    }
}

class PlayingState implements State {
    public void pressPlay(AudioPlayer player) {
        System.out.println("Pausing...");
        player.setState(new PausedState()); // Transition
    }
}

class PausedState implements State {
    public void pressPlay(AudioPlayer player) {
        System.out.println("Resuming...");
        player.setState(new PlayingState()); // Transition
    }
}

// 3. Context
class AudioPlayer {
    private State state;
    public AudioPlayer() { this.state = new StoppedState(); }
    public void setState(State s) { this.state = s; }
    public void pressPlay() { state.pressPlay(this); }
}
```

---

## ⛓️ 2. Chain of Responsibility (CoR)
> **"Pass the buck until someone handles it."**

### Concept
Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it.

### Deep Dive: Spring Security Filters
The most famous real-world example is **Spring Security**.
*   When a request hits a server, it goes through a chain:
    1.  `CorsFilter` (Checks Cross-Origin).
    2.  `CsrfFilter` (Checks CSRF Token).
    3.  `AuthenticationFilter` (Checks User/Pass).
    4.  `AuthorizationFilter` (Checks Roles).
*   If any filter fails (e.g., Bad Password), the chain stops and returns 401. If it passes, it calls `chain.doFilter()`.

### Pros & Cons
*   **Pros**: Decouples sender and receiver. You can add/remove handlers dynamically (e.g., adding a "Logging" filter in Dev environment only).
*   **Cons**: No guarantee the request will be handled (it might fall off the end of the chain). Hard to debug (Stack traces get huge).

### Code Lab
```java
abstract class LogHandler {
    protected LogHandler next;
    void setNext(LogHandler next) { this.next = next; }

    public void log(int level, String msg) {
        if (this.canHandle(level)) write(msg);
        if (next != null) next.log(level, msg); // Pass down
    }

    abstract boolean canHandle(int level);
    abstract void write(String msg);
}

class ErrorLogger extends LogHandler {
    boolean canHandle(int level) { return level == 3; }
    void write(String msg) { System.err.println("ERROR: " + msg); }
}

class FileLogger extends LogHandler {
    boolean canHandle(int level) { return level == 2; }
    void write(String msg) { System.out.println("Writing to file: " + msg); }
}
```

---

## 📝 3. Template Method
> **"Fill in the blanks."**

### Concept
Defines the skeleton of an algorithm in the superclass but lets subclasses override specific steps of the algorithm without changing its structure.

### Deep Dive: Template vs Strategy
*   **Template Method**: Uses **Inheritance**. The "skeleton" is in the Parent class. You modify parts by overriding methods. "The structure is fixed, steps vary".
*   **Strategy**: Uses **Composition**. You swap the entire algorithm object.

### Real-World Example
*   **React Component Lifecycle**: `componentDidMount`, `render`, `shouldComponentUpdate`. React (The Framework) defines *when* these are called (the template). You (The Developer) define *what* happens inside them.
*   **Data Parsers**: `openFile()` -> `parseData()` -> `analyze()` -> `closeFile()`. `open` and `close` are standard. `parse` differs for CSV vs XML.

### Code Lab
```java
abstract class DataMiner {
    // This is the Template Method. It is FINAL so subclasses can't change the flow.
    public final void mine() {
        openFile();
        extractData(); // Abstract step
        parse();       // Abstract step
        closeFile();
    }

    void openFile() { System.out.println("Opening file..."); }
    void closeFile() { System.out.println("Closing file..."); }

    abstract void extractData();
    abstract void parse();
}

class PDFMiner extends DataMiner {
    void extractData() { System.out.println("Extracting PDF text..."); }
    void parse() { System.out.println("Parsing PDF structure..."); }
}
```

---

## 🧠 Flashcards

| Question | Answer |
| :--- | :--- |
| **State Pattern** replaces what code smell? | Long `if (state == A) ... else if (state == B)` or big `switch` statements checking status. |
| **Template Method** vs **Strategy**: Key structural difference? | **Template** uses Inheritance (extends abstract class). **Strategy** uses Composition (implements interface). |
| What real-world framework uses **Chain of Responsibility** heavily? | **Spring Security** (Filter Chains) or **Servlet Filters**. |
| In **State Pattern**, who triggers the transition? | It can be the **Context** OR the **State** classes themselves (more common in complex flows). |

---

## 🛠️ Practical Task (Day 6)
**Task**: Design a **Vending Machine** using the **State Pattern**.
1.  States: `IdleState`, `HasCoinState`, `DispensingState`, `OutOfStockState`.
2.  Events: `insertCoin()`, `ejectCoin()`, `selectProduct()`, `dispense()`.
3.  **Challenge**: Implement the `selectProduct()` logic where it checks inventory. If count > 0, transition to `Dispensing`. If count == 0, transition to `OutOfStock` (or stay in HasCoin and warn user).

## 📚 Resources
*   [Refactoring Guru: State Pattern](https://refactoring.guru/design-patterns/state)
*   [SourceMaking: Chain of Responsibility](https://sourcemaking.com/design_patterns/chain_of_responsibility)
*   [Spring Security Filter Chain Documentation](https://docs.spring.io/spring-security/reference/servlet/architecture.html)
