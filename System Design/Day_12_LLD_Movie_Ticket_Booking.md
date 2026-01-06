# Day 12: LLD Practice - Movie Ticket Booking (BookMyShow)

## 🎯 Goal
Design a system with heavy concurrency requirements. The core challenge is: **"Two users clicking 'Book' on the same seat at the same time."**

---

## 🗣️ Requirements
1.  **Catalog**: Search Movies -> City -> Cinema -> ShowTime.
2.  **Selection**: User sees a seating map (Available/Booked).
3.  **Booking Flow**:
    *   User selects seats (A1, A2).
    *   System temporarily reserves them (5 mins).
    *   User pays.
    *   Booking confirmed.
4.  **Concurrency**: Strict locking. No double bookings.

---

## 💾 Database Schema (Core)

### 1. Tables
*   **Cinema**: `id, name, city_id`
*   **Screen**: `id, cinema_id, name`
*   **Seat**: `id, screen_id, row_id, number` (Physical seats)
*   **Movie**: `id, title, duration`
*   **Show**: `id, movie_id, screen_id, start_time`
*   **ShowSeat**: `id, show_id, seat_id, status (FREE, LOCKED, BOOKED), booking_id`
    *   *Note*: Separate `Seat` (physical) vs `ShowSeat` (instance for a specific time).

---

## 🔒 Concurrency Control: Handling the Race Condition

### Scenario
User A and User B select Seat A1 for Show X.

### Approach 1: Pessimistic Locking (SQL `FOR UPDATE`)
Lock the rows as soon as you read them.
```sql
BEGIN TRANSACTION;

-- Lock the rows. Other transactions WAIT.
SELECT * FROM ShowSeat
WHERE show_id = 101 AND seat_id IN (1, 2)
FOR UPDATE;

-- Check if status is FREE
IF (status == FREE) {
    UPDATE ShowSeat SET status = 'LOCKED', lock_time = NOW()
    WHERE id IN (...);
    COMMIT;
    return SUCCESS;
} ELSE {
    ROLLBACK;
    return FAIL;
}
```
*   **Pros**: 100% Safe.
*   **Cons**: Performance bottleneck. Holds DB connection open.

### Approach 2: Optimistic Locking (Versioning)
Don't lock. Just check version/state on Update.
```sql
-- Step 1: Read (No Lock)
SELECT id, status, version FROM ShowSeat WHERE id = 1;
-- Returns: status=FREE, version=5

-- Step 2: Update with Check
UPDATE ShowSeat
SET status = 'LOCKED', version = 6
WHERE id = 1 AND version = 5; -- The crucial check!

-- Step 3: Check result
-- If 1 row updated -> Success.
-- If 0 rows updated -> Someone else changed version to 6. Fail.
```
*   **Pros**: Faster reads. No DB locking. Good for low contention.
*   **Cons**: User might fail at the very end.

**Verdict for Movie Booking**: Use **Optimistic Locking** or **Pessimistic Locking with Timeout**. Given the high contention on blockbuster releases, Redis-based locking is often preferred in modern systems.

---

## 🏗️ Class Design

```java
class BookingService {

    public Booking reserveSeats(int showId, List<Integer> seatIds, int userId) {
        // 1. Transaction Start
        // 2. Fetch ShowSeats
        // 3. Check if ALL are FREE
        // 4. Update status = LOCKED, set temp_booking_id
        // 5. Commit
        // 6. Start async timer to expire lock after 5 mins

        return new Booking(id, status: PENDING_PAYMENT);
    }

    public void confirmBooking(int bookingId) {
        // 1. Check if payment success
        // 2. Update ShowSeat status = BOOKED
    }
}
```

---

## 🧠 Interview Nuances

### 1. How to handle "Hold for 5 mins"?
*   **Redis Keys**: `SET seat_lock:{showID}:{seatID} {userID} EX 300 NX`
    *   `EX 300`: Expire in 300 seconds.
    *   `NX`: Only set if Not Exists.
*   If Redis `SET` returns OK, you got the lock.
*   If null, someone else has it.

### 2. Isolation Levels
*   If using SQL, ensure Isolation Level is `Serializable` or `Repeatable Read` to prevent Phantom Reads (though explicit locking avoids this).

---

## 🛠️ Practical Task
1.  Write the **SQL Queries** for the Optimistic Locking approach.
2.  Design the **API Endpoints**:
    *   `GET /shows/{id}/seats` (What does the response JSON look like?)
    *   `POST /bookings/reserve`
    *   `POST /bookings/confirm`
