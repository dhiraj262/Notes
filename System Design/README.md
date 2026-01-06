# System Design Learning Plan (2 Months)

This comprehensive 60-day plan covers **High-Level Design (HLD)**, **Low-Level Design (LLD)**, and **Object-Oriented Design (OOD)** to prepare you for system design interviews and real-world engineering challenges.

## Goals
1.  Master fundamental System Design concepts (Scalability, Availability, Consistency).
2.  Proficiency in LLD/OOD (Design Patterns, Schema Design, Code modularity).
3.  Ability to design large-scale systems (e.g., Uber, Twitter) end-to-end.
4.  Retention through active recall (Flashcards, Mock Interviews).

## Recommended Resources
*   **Books**:
    *   *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann (The Bible of HLD).
    *   *System Design Interview – An Insider's Guide* (Vol 1 & 2) by Alex Xu.
    *   *Head First Design Patterns* (for LLD).
*   **Websites & Repos**:
    *   [System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer)
    *   [Refactoring.guru](https://refactoring.guru/design-patterns) (Excellent for Design Patterns).
    *   [High Scalability](http://highscalability.com/) (Real-world case studies).
    *   [LeetCode Discuss](https://leetcode.com/discuss/interview-question?currentPage=1&orderBy=most_relevant&query=system%20design) (Recent interview questions).

---

## Phase 1: Foundations, OOD & LLD (Days 1-20)

### Week 1: OOP Principles & Design Patterns Basics
*   **Day 1**: **OOP Principles Review**. Encapsulation, Abstraction, Inheritance, Polymorphism.
    *   *Task*: Explain these concepts to a friend or rubber duck.
*   **Day 2**: **SOLID Principles**. S.O.L.I.D deeply explained with code examples.
    *   *Resource*: DigitalOcean/GeeksForGeeks articles on SOLID.
*   **Day 3**: **UML Basics**. Class diagrams, Sequence diagrams, Activity diagrams.
    *   *Task*: Draw a class diagram for a simple Library Management System.
*   **Day 4**: **Creational Design Patterns**. Singleton, Factory, Builder.
    *   *Ref*: Refactoring.guru.
*   **Day 5**: **Structural Design Patterns**. Adapter, Decorator, Facade, Proxy.
*   **Day 6**: **Behavioral Design Patterns**. Observer, Strategy, Command.
*   **Day 7**: **Review & Flashcards**. Create Anki cards for patterns and SOLID principles.
    *   *Project*: Implement a simple Logger using Singleton and Chain of Responsibility.

### Week 2: Advanced LLD & Schema Design
*   **Day 8**: **Concurrency & Multithreading**. Threads, Locks, Synchronization, Thread Pool.
*   **Day 9**: **Database Schema Design**. ER Diagrams, Normalization (1NF, 2NF, 3NF).
    *   *Task*: Design DB schema for an E-commerce Order system.
*   **Day 10**: **LLD Problem: Parking Lot**.
    *   *Focus*: Classes (Vehicle, Spot, Ticket), Interfaces, Extensibility.
*   **Day 11**: **LLD Problem: Elevator System**.
    *   *Focus*: State Pattern, Scheduling algorithms.
*   **Day 12**: **LLD Problem: Movie Ticket Booking System** (BookMyShow).
    *   *Focus*: Concurrency (locking seats).
*   **Day 13**: **LLD Problem: Design a Game** (Chess/Tic-Tac-Toe/Deck of Cards).
    *   *Focus*: Game loop, Object interactions.
*   **Day 14**: **Code Review Simulation**. Take your code from Day 10-13, critique it against SOLID principles.

### Week 3: LLD Wrap-up & Transition to HLD
*   **Day 15**: **API Design**. REST vs GraphQL vs gRPC. Best practices for URL naming, versioning.
*   **Day 16**: **Caching Strategies (LLD Level)**. LRU Cache implementation.
    *   *Task*: Implement LRU Cache in code (LeetCode #146).
*   **Day 17**: **Rate Limiter (LLD)**. Token Bucket, Leaky Bucket algorithms implementation.
*   **Day 18**: **Testing**. Unit Testing (JUnit/PyTest), Mocking.
*   **Day 19**: **LLD Mock Interview**. Find a peer or use a platform like Pramp.
*   **Day 20**: **Buffer Day / Revision**. Review weak spots in Design Patterns.

---

## Phase 2: High-Level Design (HLD) Components (Days 21-40)

### Week 4: HLD Core Concepts
*   **Day 21**: **Scalability Basics**. Vertical vs Horizontal Scaling, Latency vs Throughput.
    *   *Reading*: DDIA Chapter 1.
*   **Day 22**: **Load Balancing**. L4 vs L7 LB, Algorithms (Round Robin, Least Conn). Nginx/HAProxy.
*   **Day 23**: **Databases**. SQL vs NoSQL (Document, Columnar, Key-Value, Graph). ACID vs BASE.
    *   *Task*: Create a comparison chart of PostgreSQL, MongoDB, Cassandra, Redis.
*   **Day 24**: **Database Replication & Sharding**. Master-Slave, Master-Master, Partitioning strategies.
*   **Day 25**: **CAP Theorem & PACELC**. Understanding trade-offs in distributed systems.
*   **Day 26**: **Caching (System Level)**. Write-through, Write-back, Write-around. Redis/Memcached.
    *   *Problem*: How to handle cache stampede?
*   **Day 27**: **Consistent Hashing**. Why it's needed for distributed caching/storage.
    *   *Task*: Watch a video explanation and implement a toy version.

### Week 5: Advanced Distributed Components
*   **Day 28**: **Message Queues**. Kafka, RabbitMQ. Pub-Sub model. Async processing.
*   **Day 29**: **Content Delivery Network (CDN)**. How CDNs work (Push vs Pull). Edge locations.
*   **Day 30**: **Unique ID Generators**. UUID, Snowflake, Ticket Server.
*   **Day 31**: **Distributed Transactions**. Two-Phase Commit (2PC), Sagas Pattern.
*   **Day 32**: **Monitoring & Alerting**. Metrics (Prometheus), Logging (ELK Stack), Tracing.
*   **Day 33**: **Security Basics**. HTTPS, TLS, OAuth 2.0, JWT.
*   **Day 34**: **Search Engines**. Inverted Index, Elasticsearch basics.

### Week 6: Mini-Projects & Consolidation
*   **Day 35**: **Project: URL Shortener (TinyURL)**.
    *   *Focus*: Hashing, Database choice, Scale estimation.
*   **Day 36**: **Project: Pastebin**.
    *   *Focus*: Storage cost estimation, Expiration policy.
*   **Day 37**: **Project: Notification System**.
    *   *Focus*: Message Queues, Push vs Pull.
*   **Day 38**: **Back-of-the-envelope Math**. Review powers of two, latency numbers (RAM vs Disk vs Network).
*   **Day 39**: **Review Week 4-5**. Flashcard blast.
*   **Day 40**: **Buffer Day**. Read a random "High Scalability" article.

---

## Phase 3: Real-World HLD System Design (Days 41-60)

### Week 7: The "Design X" Questions
*   **Day 41**: **Design a Chat Application (WhatsApp/Messenger)**.
    *   *Key*: WebSockets, Message storage, Online status.
*   **Day 42**: **Design a Social Media Feed (Twitter/Facebook)**.
    *   *Key*: Fan-out service (Push vs Pull), Feed generation.
*   **Day 43**: **Design a Video Streaming Service (YouTube/Netflix)**.
    *   *Key*: Chunking, Transcoding, CDN usage, Adaptive Bitrate Streaming.
*   **Day 44**: **Design a Ride-Sharing App (Uber/Lyft)**.
    *   *Key*: Geo-hashing (QuadTree/Google S2), Location updates, Matching logic.
*   **Day 45**: **Design an E-commerce Store (Amazon)**.
    *   *Key*: Inventory management (concurrency), Shopping cart, Checkout flow.
*   **Day 46**: **Design a Web Crawler (Google Search)**.
    *   *Key*: Politeness, URL Frontier, DNS resolution, Deduplication.
*   **Day 47**: **Design a Typeahead/Autocomplete System**.
    *   *Key*: Trie data structure, Top-k heavy hitters.

### Week 8: Advanced Scenarios & Final Polish
*   **Day 48**: **Design Google Maps**.
    *   *Key*: Graph algorithms (Dijkstra/A*), Tile serving.
*   **Day 49**: **Design a Rate Limiter (API Gateway)**.
    *   *Key*: Distributed counting, Sliding window log.
*   **Day 50**: **Design Distributed Job Scheduler**.
    *   *Key*: Leader election, Cron parsing.
*   **Day 51**: **Mock Interview 1**. Focus on Requirements Gathering and Scope definition.
*   **Day 52**: **Mock Interview 2**. Focus on HLD Diagramming and Trade-off discussions.
*   **Day 53**: **Mock Interview 3**. Focus on Deep Dive and Bottleneck identification.
*   **Day 54**: **Read: Google File System (GFS) Paper**. Or BigTable paper.
*   **Day 55**: **Read: Dynamo Paper (Amazon)**. Understanding eventual consistency history.
*   **Day 56**: **Final Project: Design YOUR System**.
    *   *Task*: Pick a system you use (e.g., Spotify) and write a full design doc.
*   **Day 57**: **Review: Failure Scenarios**. What if the DB dies? What if the cache fills up?
*   **Day 58**: **Behavioral Prep**. "Tell me about a time you designed a difficult system."
*   **Day 59**: **Rest & Light Review**. Review your cheat sheets.
*   **Day 60**: **Ready**. You are prepared.

---

## Retention Strategies
1.  **Flashcards**: Use Anki. Create cards for every new term (e.g., "What is Consistent Hashing?", "Pros/Cons of NoSQL").
2.  **Feynman Technique**: After every topic, try to explain it simply (out loud or writing) as if teaching a junior engineer.
3.  **Spaced Repetition**: Re-visit Day 1-10 topics on Day 20, 30, and 50.
4.  **Implement It**: Don't just draw boxes. Code a simple Redis-backed cache or a WebSocket chat server.

## Daily Routine Template
*   **30 Mins**: Read/Watch concept (YouTube/Book).
*   **30 Mins**: Active Note-taking (summarize in your own words).
*   **45 Mins**: Problem Solving / Diagramming / Coding.
*   **15 Mins**: Review Flashcards.
