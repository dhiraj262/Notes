# Day 7: LLD Practice - Parking Lot System

## 🎯 Goal
Design a Parking Lot system. This is the #1 most asked LLD question.
**Focus**: Classes, Interfaces, Enums, and Relationships.

---

## 🗣️ Requirements
1.  **Multiple Levels**: The parking lot has multiple floors.
2.  **Spot Types**: Compact, Large, Handicapped, Motorcycle.
3.  **Vehicle Types**: Car (fits Compact/Large), Truck (fits Large), Bike (fits Motorcycle).
4.  **Entry/Exit**: Multiple entry and exit gates.
5.  **Ticket**: System issues a ticket on entry and calculates fee on exit.
6.  **Display**: Show free spots per floor.

---

## 📐 Class Diagram (Mental Model)

### Core Classes
1.  **ParkingLot**: Singleton? Or just a main class. Contains `List<ParkingFloor>`.
2.  **ParkingFloor**: Contains `List<ParkingSpot>` and a `DisplayBoard`.
3.  **ParkingSpot**: Base class.
    *   `CompactSpot`, `LargeSpot`, `HandicappedSpot`.
    *   Properties: `id`, `isFree`, `SpotType`.
4.  **Vehicle**: Abstract class.
    *   `Car`, `Truck`, `Bike`.
    *   Properties: `licensePlate`, `VehicleType`.
5.  **Ticket**: `id`, `entryTime`, `spotId`.
6.  **Gate**: `EntryGate`, `ExitGate`.

---

## 💻 Code Skeleton (Java)

```java
// Enums
enum VehicleType { CAR, TRUCK, BIKE }
enum SpotType { COMPACT, LARGE, HANDICAPPED, MOTORCYCLE }

// Vehicle Hierarchy
abstract class Vehicle {
    private String licensePlate;
    private VehicleType type;
    public Vehicle(VehicleType type) { this.type = type; }
    public VehicleType getType() { return type; }
}

class Car extends Vehicle {
    public Car() { super(VehicleType.CAR); }
}

// Spot Hierarchy
class ParkingSpot {
    private int id;
    private SpotType type;
    private boolean isFree;
    private Vehicle vehicle;

    public boolean assignVehicle(Vehicle v) {
        this.vehicle = v;
        this.isFree = false;
        return true;
    }

    public void removeVehicle() {
        this.vehicle = null;
        this.isFree = true;
    }
}

// The Parking Lot
class ParkingLot {
    private static ParkingLot instance = null;
    private List<ParkingFloor> floors;

    private ParkingLot() { floors = new ArrayList<>(); }

    public static ParkingLot getInstance() {
        if (instance == null) instance = new ParkingLot();
        return instance;
    }

    public Ticket parkVehicle(Vehicle v) {
        // 1. Find a free spot for this vehicle type
        // 2. If found, create Ticket
        // 3. Mark spot as occupied
        // 4. Return Ticket
    }
}
```

---

## 🧠 Key Design Decisions (Interview Prep)
1.  **How to handle concurrency?**
    *   If two cars try to book the same spot?
    *   *Solution*: Use `synchronized` on the method finding the spot, or use a `ConcurrentHashMap` / `BlockingQueue` for available spots.
2.  **Pricing Strategy?**
    *   Use the **Strategy Pattern**. `PricingStrategy` interface with `HourlyPricing`, `DailyPricing`. Pass the strategy to the `ExitGate` or `Ticket`.
3.  **Find nearest spot?**
    *   Use a **Min-Heap** for each floor to store free spots ordered by distance from entrance.

---

## 🛠️ Practical Task
1.  Complete the `parkVehicle` method.
2.  Implement `calculateFee(Ticket t)` using a Strategy pattern ($2 first hour, $1 subsequent).
