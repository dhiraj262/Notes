# Day 20: LLD Practice - Tic-Tac-Toe / Chess

## 🎯 Goal
Design a Board Game (Tic-Tac-Toe or Chess). This tests your ability to model **Game States**, **Rules**, and **Turn Management**.
**Focus**: Game Loop, Separation of Concerns (UI vs Logic), and Extensibility.

---

## 🧩 Key Concepts

### 1. The Game Loop
Core flow of any game:
1.  **Render**: Show the board.
2.  **Input**: Get move from current player.
3.  **Update**: Validate move -> Update Board State -> Check Win Condition -> Switch Player.
4.  **Repeat**.

### 2. Representing the Board
*   **Tic-Tac-Toe**: `char[3][3]` or `Piece[3][3]`.
*   **Chess**: `Piece[8][8]`.
*   **Optimization**: Bitboards (using 64-bit integers) for high-performance chess engines.

### 3. Move Validation
*   **Tic-Tac-Toe**: Is cell empty? Is it within bounds?
*   **Chess**:
    *   **Generic**: In bounds? Not taking own piece?
    *   **Piece Specific**: Rook moves straight, Bishop diagonal.
    *   **State Specific**: Does this move leave King in check?

---

## 🏗️ Class Design (Chess Focus)

### 1. Enums
```java
enum Color { WHITE, BLACK }
enum GameStatus { ACTIVE, BLACK_WIN, WHITE_WIN, STALEMATE }
```

### 2. The Pieces (Polymorphism)
```java
abstract class Piece {
    Color color;
    boolean isKilled = false;

    public abstract boolean canMove(Board board, Box start, Box end);
}

class King extends Piece {
    // Implement Castling logic here
    public boolean canMove(Board board, Box start, Box end) {
        // Logic for King's movement (1 step in any direction)
    }
}
```

### 3. The Board & Box
```java
class Box {
    int x, y;
    Piece piece; // Null if empty
}

class Board {
    Box[][] boxes = new Box[8][8];

    public void resetBoard() {
        // Initialize pieces
    }
    public void move(Move move) {
        // Execute move, kill piece if necessary
    }
}
```

### 4. The Player & Move
```java
class Player {
    boolean whiteSide;
    boolean humanPlayer; // vs AI
}

class Move {
    Player player;
    Box start;
    Box end;
    Piece pieceMoved;
    Piece pieceKilled;
}
```

### 5. Game Controller (Singleton/Driver)
```java
class Game {
    Board board;
    Player[] players;
    GameStatus status;
    List<Move> movesPlayed;

    public void playerMove(Player player, int startX, int startY, int endX, int endY) {
        Box startBox = board.getBox(startX, startY);
        Box endBox = board.getBox(endX, endY);
        Move move = new Move(player, startBox, endBox);

        if (validateMove(move)) {
             board.move(move);
             movesPlayed.add(move);
             if (checkWin()) status = ...;
        }
    }
}
```

---

## 🧠 Design Patterns

### 1. Command Pattern
Each `Move` is a Command.
*   Allows **Undo/Redo** functionality (Stack of Moves).
*   Allows sending moves over network (Serialization).

### 2. Strategy Pattern
*   Used for **Move Validation** if rules vary (e.g., Variant Chess).
*   Used for **AI Player** logic (EasyBot vs HardBot).

### 3. Observer Pattern
*   The `Board` notifies the `UI` when state changes (Piece moved, Checkmate).

---

## 🛠️ Practical Task
**Task**: Implement the `canMove` logic for a **Knight** in Chess.
*   *Knight Logic*: 'L' shape. 2 steps in one direction, 1 step perpendicular.
*   *Math*: `|dx| * |dy| == 2`. (i.e., 1x2 or 2x1).

**Task 2**: Design `Tic-Tac-Toe` with an **Undo** feature.
*   Use a `Stack<Move>`.
*   `undo()`: Pop move, revert board state (set cell to empty), switch turn back.
