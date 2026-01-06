# Day 11: LLD Practice - Elevator System

## 🎯 Goal
Design a Smart Elevator System. This is a classic "State-Based" and "Scheduling" problem.
**Focus**: State Pattern, Scheduling Algorithms, and Object interactions.

---

## 🗣️ Requirements
1.  **Multiple Elevators**: A building has `N` elevators.
2.  **Requests**:
    *   **External Request**: User on Floor 5 presses "UP". (Source Floor, Direction)
    *   **Internal Request**: User inside Elevator 1 presses "Floor 10". (Destination Floor)
3.  **Optimization**: Minimize wait time and power usage.
4.  **Constraints**: Capacity limit (weight/people).

---

## 🧠 Scheduling Algorithms
The brain of the elevator. How does it decide where to go next?

### 1. FCFS (First Come First Serve)
*   **Logic**: Process requests in order of arrival.
*   **Problem**: If Elevator is at Floor 1, Req 1: Floor 10, Req 2: Floor 2. It goes 1 -> 10 -> 2. Huge waste.

### 2. SCAN (The "Elevator" Algorithm)
*   **Logic**: Move entirely in one direction (e.g., UP), servicing all requests in that direction. When top reached, switch to DOWN.
*   **Problem**: Goes to top even if no requests there.

### 3. LOOK (Optimized SCAN) - **Preferred**
*   **Logic**: Like SCAN, but if there are no pending requests ahead in the current direction, reverse direction immediately.

---

## 🏗️ Class Design

### 1. Enums & Helpers
```java
enum Direction { UP, DOWN, IDLE }
enum State { MOVING, IDLE, STOPPED }
```

### 2. Request Classes
```java
class Request {
    int floor;
    // For External: user wants to go UP/DOWN from here
    // For Internal: user wants to go TO here
    Direction desiredDirection;
    long timestamp;

    // Constructor...
}
```

### 3. The Elevator (State & Logic)
```java
class Elevator {
    int id;
    int currentFloor;
    Direction currentDirection;
    State state;

    // Min-Heap for UP requests (Closest floor first)
    PriorityQueue<Integer> upQueue = new PriorityQueue<>();

    // Max-Heap for DOWN requests (Closest floor first)
    PriorityQueue<Integer> downQueue = new PriorityQueue<>((a,b) -> b - a);

    public void addRequest(int floor) {
        if (floor == currentFloor) return; // Open doors

        if (floor > currentFloor) upQueue.add(floor);
        else downQueue.add(floor);

        if (state == State.IDLE) {
            // Wake up logic: Set direction based on new request
            currentDirection = (floor > currentFloor) ? Direction.UP : Direction.DOWN;
            state = State.MOVING;
        }
    }

    public void move() {
        // LOOK Algorithm Logic
        if (currentDirection == Direction.UP) {
            if (upQueue.isEmpty()) {
                currentDirection = Direction.DOWN; // Reverse
                return;
            }
            int nextStop = upQueue.poll();
            moveTo(nextStop);
        } else {
            // Similar logic for DOWN
        }
    }
}
```

### 4. Dispatcher (The Manager)
Handles **External Requests** and assigns them to the "Best" elevator.

```java
class Dispatcher {
    List<Elevator> elevators;

    public void dispatch(int sourceFloor, Direction dir) {
        // Strategy:
        // 1. Find an elevator moving in SAME direction that hasn't passed sourceFloor.
        // 2. OR find an IDLE elevator.
        // 3. Assign the request to that elevator's queue.

        Elevator bestLift = findBestElevator(sourceFloor, dir);
        bestLift.addRequest(sourceFloor);
    }
}
```

---

## 🧠 Interview Nuances

### 1. The "State Pattern"
Instead of `if (state == MOVING)`, use classes:
*   `IdleState`: `processRequest()` -> transitions to `MovingState`.
*   `MovingState`: `reachFloor()` -> transitions to `StoppedState`.
*   `StoppedState`: `doorOpen()` -> `doorClose()` -> transitions to `Moving` or `Idle`.

### 2. Threading
*   Each Elevator runs on its own **Thread**.
*   The `Dispatcher` is the main controller.
*   Use `synchronized` when adding requests to the queues.

---

## 🛠️ Practical Task
**Task**: Implement the `findBestElevator` logic in the Dispatcher.
*   *Input*: Request(Floor 5, UP).
*   *Elevator A*: Floor 2, UP. (Score: Good)
*   *Elevator B*: Floor 7, UP. (Score: Bad - passed it)
*   *Elevator C*: Floor 4, DOWN. (Score: Bad - wrong way)
*   *Elevator D*: IDLE. (Score: Okay)

Write the logic to pick **Elevator A**.
