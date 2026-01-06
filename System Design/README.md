# System Design Learning Plan (3 Months)

This comprehensive 90-day plan covers **High-Level Design (HLD)**, **Low-Level Design (LLD)**, **Object-Oriented Design (OOD)**, and **AI/ML System Design**. It is designed to prepare you for senior engineering interviews and real-world architecture challenges.

## Goals
1.  **Foundational Mastery**: Deep understanding of OOD, Design Patterns, and DB Internals.
2.  **Distributed Systems**: Mastery of scalability, consistency, and availability trade-offs.
3.  **AI/ML Competence**: Ability to design machine learning systems (Recommenders, LLM apps).
4.  **Retention**: Active recall through flashcards, teaching, and implementation.

## 📚 Top Quality Resources

### Books
*   **The Bible**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann.
*   **HLD**: *System Design Interview – An Insider's Guide* (Vol 1 & 2) by Alex Xu.
*   **LLD**: *Head First Design Patterns* or *Clean Architecture* by Uncle Bob.
*   **AI**: *Machine Learning System Design Interview* by Alex Xu & Ali Aminian.

### Websites & GitHub Repos
*   [System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer) - The gold standard.
*   [Refactoring.guru](https://refactoring.guru/design-patterns) - Best for LLD/Patterns.
*   [Tech Interview Handbook](https://github.com/yangshun/tech-interview-handbook) - Comprehensive guide.
*   [ML System Design (GitHub)](https://github.com/alirezadir/Machine-Learning-Interviews) - For the AI section.
*   [High Scalability](http://highscalability.com/) - Real-world case studies.

### 📰 Must-Read Newsletters
Stay updated with industry trends by subscribing to these:
1.  **ByteByteGo** (Alex Xu) - Visual system design explanations.
2.  **The Pragmatic Engineer** (Gergely Orosz) - Engineering culture & trends.
3.  **System Design Newsletter** (Neo Kim) - Deep dives into specific architectures.
4.  **The Polymathic Engineer** - Algorithms & Distributed Systems.
5.  **Big Tech Digest** - Aggregated tech blog posts from huge companies.

---

## Month 1: Foundations, OOD & Database Internals (Days 1-30)

### Week 1: OOD & Design Patterns (The "Code" Layer)
*   **Day 1: SOLID Principles**. Deep dive into SRP, OCP, LSP, ISP, DIP.
    *   *Task*: Refactor a bad piece of code to follow SOLID.
*   **Day 2: UML & Class Diagrams**. Relationships (Association, Aggregation, Composition).
*   **Day 3: Creational Patterns**. Singleton, Factory, Builder.
*   **Day 4: Structural Patterns**. Adapter, Decorator, Facade.
*   **Day 5: Behavioral Patterns I**. Observer, Strategy (crucial for payment systems).
*   **Day 6: Behavioral Patterns II**. Command, State (crucial for Order/Ride status).
*   **Day 7: LLD Practice**. Design a **Parking Lot** (Classes, Interfaces).

### Week 2: Concurrency & OS Basics
*   **Day 8: Processes vs Threads**. Stack vs Heap. Context Switching.
*   **Day 9: Concurrency Primitives**. Locks, Mutex, Semaphores, Monitors.
*   **Day 10: Deadlocks & Race Conditions**. How to prevent them.
*   **Day 11: Java/Python Concurrency**. Thread Pools, Futures, CompletableFuture.
*   **Day 12: LLD Practice**. Design a **Task Scheduler** or **Rate Limiter (Class Level)**.
*   **Day 13: LLD Practice**. Design a **Movie Ticket Booking System** (Handling concurrency).
*   **Day 14: Review**. Flashcards on Patterns & Concurrency.

### Week 3: Database Internals (The "Data" Layer)
*   **Day 15: Storage Engines**. LSM Trees (Cassandra/Kafka) vs B-Trees (SQL/Mongo).
    *   *Reading*: DDIA Chapter 3.
*   **Day 16: Indexing**. Hash Indexes, SSTables, Bloom Filters.
*   **Day 17: Transactions (ACID)**. Atomicity, Isolation Levels (Read Committed, Serializable).
*   **Day 18: NoSQL Types**. Document, Column-family, Graph, Key-Value. When to use what?
*   **Day 19: SQL vs NoSQL Modeling**. Normalization vs Denormalization.
*   **Day 20: LLD Practice**. Design **Tic-Tac-Toe** or **Chess** (Game Loop, State).

### Week 4: LLD Wrap-up & Transition
*   **Day 21: API Design**. REST (Resources, Verbs) vs GraphQL (Schema, Resolvers).
*   **Day 22: gRPC & Protocol Buffers**. High-performance inter-service communication.
*   **Day 23: Testing Strategies**. Unit, Integration, End-to-End. TDD basics.
*   **Day 24: Code Quality**. DRY, KISS, YAGNI. Code Review checklist.
*   **Day 25: LLD Mock Interview**. Peer mock: "Design an Elevator System".
*   **Day 26-30: Buffer/Review**. Catch up on DDIA reading. Build a simple CLI tool.

---

## Month 2: Core HLD & Distributed Systems (Days 31-60)

### Week 5: Distributed Foundations
*   **Day 31: Scalability**. Vertical (Scale-up) vs Horizontal (Scale-out).
*   **Day 32: Load Balancing**. L4 vs L7. Algorithms (Round Robin, Consistent Hashing).
*   **Day 33: Replication**. Single-Leader, Multi-Leader, Leaderless.
    *   *Reading*: DDIA Chapter 5.
*   **Day 34: Partitioning/Sharding**. Key-based, Range-based. Rebalancing.
*   **Day 35: CAP & PACELC**. Consistency vs Availability.
*   **Day 36: Caching Patterns**. Cache-Aside, Write-Through. Redis/Memcached internals.
*   **Day 37: Design Case**. **URL Shortener (TinyURL)**.

### Week 6: Async & Consistency
*   **Day 38: Message Queues**. Kafka vs RabbitMQ. Topics, Partitions, Offset.
*   **Day 39: Event-Driven Architecture**. Pub-Sub pattern.
*   **Day 40: Distributed Transactions**. 2PC, Sagas (Choreography vs Orchestration).
*   **Day 41: Idempotency**. Why it matters in payments and messaging.
*   **Day 42: Unique ID Generation**. Snowflake, UUID.
*   **Day 43: Consistency Models**. Strong, Eventual, Causal.
*   **Day 44: Design Case**. **Notification System**.

### Week 7: Core System Design Cases
*   **Day 45: Design a Chat App (WhatsApp)**. WebSockets, Message storage.
*   **Day 46: Design a Rate Limiter (Distributed)**. Redis + Lua script.
*   **Day 47: Design a Key-Value Store**. Replication, Tunable consistency (Quorums).
*   **Day 48: Design a Web Crawler**. URL Frontier, Politeness, Parsing.
*   **Day 49: Design Youtube/Netflix**. CDN, Transcoding, Adaptive Streaming.
*   **Day 50: Design Google Drive**. Chunking, Deduplication, Sync.
*   **Day 51: Review**. Review detailed notes on the above cases.

### Week 8: Advanced Data Systems
*   **Day 52: Search Engines**. Inverted Index, Elasticsearch, Lucene segments.
*   **Day 53: Design Typeahead**. Tries, Top-K problems.
*   **Day 54: Distributed Logging & Monitoring**. ELK Stack, Prometheus, Grafana.
*   **Day 55: Batch vs Stream Processing**. Hadoop/MapReduce vs Flink/Spark Streaming.
    *   *Reading*: DDIA Chapter 10.
*   **Day 56: Geo-Spatial Indexing**. QuadTrees, Google S2.
*   **Day 57: Design Uber/Lyft**. Location updates, Matchmaking.
*   **Day 58-60: Buffer/Review**.

---

## Month 3: AI/ML Systems & Advanced Topics (Days 61-90)

### Week 9: AI System Design Basics
*   **Day 61: ML Pipeline Overview**. Data Collection -> Training -> Evaluation -> Deployment.
*   **Day 62: Training vs Inference**. Batch prediction vs Online prediction.
*   **Day 63: Model Serving Patterns**. Model-as-a-Service, Embedded model.
*   **Day 64: Feature Stores**. What is it? (e.g., Tecton, Feast). Offline/Online skew.
*   **Day 65: Monitoring ML**. Data Drift, Concept Drift, Model Decay.
*   **Day 66: Evaluation Metrics**. Precision, Recall, F1, ROC-AUC.
*   **Day 67: AI Design Case**. **Ad Click Prediction**. High QPS, Low Latency.

### Week 10: Designing Recommender Systems
*   **Day 68: Recommendation Basics**. Collaborative Filtering vs Content-Based.
*   **Day 69: Two-Tower Architecture**. Candidate Generation -> Ranking -> Re-ranking.
*   **Day 70: Embeddings & Vector DBs**. FAISS, Pinecone, Milvus. Approximate Nearest Neighbor (ANN).
*   **Day 71: Design Case**. **News Feed (Facebook/Twitter)**.
*   **Day 72: Design Case**. **Video Recommendation (TikTok/YouTube)**.
*   **Day 73: Design Case**. **People You May Know (LinkedIn Graph)**.
*   **Day 74: Review**. Deep dive into "Machine Learning System Design Interview" book resources.

### Week 11: LLM & GenAI Systems (The Cutting Edge)
*   **Day 75: LLM Basics for Systems**. Context window, Tokens, Temperature.
*   **Day 76: RAG Architecture (Retrieval-Augmented Generation)**. Vector DB + LLM.
*   **Day 77: Inference Optimization**. KV Caching, Quantization, Speculative Decoding.
*   **Day 78: Design Case**. **ChatGPT-like Assistant**. History management, Streaming tokens.
*   **Day 79: Design Case**. **Code Copilot**. Context awareness, Latency constraints.
*   **Day 80: Agents & Tool Use**. ReAct pattern, LangChain concepts.
*   **Day 81: AI Safety & Limits**. Rate limiting expensive models, Hallucination guardrails.

### Week 12: Final Polish & Mock Interviews
*   **Day 82: Mock Interview (LLD)**. Focus on clean code and patterns.
*   **Day 83: Mock Interview (HLD - Standard)**. Focus on "Design Twitter".
*   **Day 84: Mock Interview (HLD - AI)**. Focus on "Design a Recommender".
*   **Day 85: Behavioral Prep**. STAR Method. "Tell me about a conflict."
*   **Day 86: Resume Walkthrough**. Prepare deep technical explanations for your past projects.
*   **Day 87: Failure Scenarios**. "What if the Leader crashes?" "What if the Region goes down?"
*   **Day 88: Newsletter Catch-up**. Read the last 3 issues of ByteByteGo/Pragmatic Engineer.
*   **Day 89: Rest & Light Review**. Visualizing systems with eyes closed.
*   **Day 90: READY**. You are now a System Design expert.

---

## Daily Routine for Success
1.  **Input (30m)**: Read 1 article or watch 1 video from the resources.
2.  **Process (30m)**: Summarize the concept in your own words (Feynman technique).
3.  **Output (1h)**: Solve a problem, draw a diagram, or write code.
4.  **Recall (15m)**: Review Anki flashcards before bed.
