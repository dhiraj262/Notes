# GraphRAG: From Local to Global Context

## 1. Latest Context
As of early 2025, Retrieval-Augmented Generation (RAG) is the standard for grounding LLMs in private data. However, standard RAG (or "Baseline RAG") faces a critical ceiling: it excels at **local** retrieval ("What is the flight time?") but fails at **global** summarization ("What are the main themes in these 1,000 documents?").

**GraphRAG** (Graph-based Retrieval-Augmented Generation), pioneered by Microsoft Research and now a top trending architecture on GitHub, solves this by combining **Knowledge Graphs** with LLMs. It moves beyond simple vector similarity to structured, hierarchical understanding, enabling "Global Sensemaking" over massive datasets.

## 2. What, Why, How

### What is GraphRAG?
GraphRAG is a pipeline that transforms unstructured text into a structured **Knowledge Graph**.
*   It doesn't just chunk text and embed it.
*   It uses an LLM to extract **Entities** (People, Places, Concepts) and **Relationships** (How they connect).
*   It detects **Communities** (clusters of related entities) and generates hierarchical summaries for each community.

### Why do we need it?
*   **The "Global Question" Problem**: Standard RAG retrieves the "Top-K" chunks. If the answer requires connecting dots across 50 different documents (e.g., "How has the sentiment towards AI changed in 2024?"), standard RAG misses the forest for the trees.
*   **Hallucination in Summarization**: When asked to summarize a huge corpus, standard LLMs run out of context window or get lost. GraphRAG uses pre-generated community summaries to provide a grounded, comprehensive answer.

### How does it work? (The Pipeline)
1.  **Index Phase**:
    *   **Extraction**: LLM reads documents and identifies entities (Nodes) and relationships (Edges).
    *   **Graph Building**: A graph is constructed (e.g., NetworkX).
    *   **Community Detection**: Algorithms (like Leiden) partition the graph into hierarchical communities (clusters).
    *   **Summarization**: An LLM generates a summary for each community.
2.  **Query Phase**:
    *   **Global Search**: For high-level questions, the system aggregates the *community summaries* rather than raw text chunks to generate an answer.
    *   **Local Search**: For specific questions, it can still traverse the graph to find connected entities.

## 3. Use Cases
GraphRAG is essential for "Discovery" and "Sensemaking" tasks.

*   **Intelligence & Security**: Analyzing thousands of intelligence reports to identify emerging threat narratives that span multiple unconnected incidents.
*   **Scientific Research**: Reviewing literature to find connections between proteins, diseases, and drugs that are never mentioned in the same paper but are linked via intermediaries.
*   **Legal Discovery**: Understanding the relationship web in massive email dumps (Enron style) to identify key players and hidden alliances.
*   **Financial Analysis**: Aggregating news across an entire sector to determine macro-trends rather than just analyzing individual stock performance.

## 4. Real World Examples

### Example 1: The "Podcast" Analysis (Microsoft Benchmark)
*   **Dataset**: Transcripts of the Kevin Scott (Microsoft CTO) podcast.
*   **Query**: "What do these tech leaders say about the future of AI?"
*   **Baseline RAG Result**: Retrieves a few specific quotes about AI from random episodes. Result is disjointed.
*   **GraphRAG Result**: Identifies clusters (Ethics, scaling, hardware). It synthesizes a structured essay explaining that "Leaders generally agree on scaling laws but diverge on timeline and safety," citing specific clusters of conversation.

### Example 2: Medical "Drug Repurposing"
*   **Task**: Find if a drug used for Heart Disease might help with Alzheimer's.
*   **GraphRAG**:
    *   Doc A: "Drug X reduces Protein Y."
    *   Doc B: "Protein Y is found in Alzheimer's plaques."
    *   **Graph**: Drug X --(reduces)--> Protein Y --(linked to)--> Alzheimer's.
    *   **Result**: The graph reveals the path that vector search (which looks for "Drug X" and "Alzheimer's" co-occurring) would miss.

## 5. Future Readiness & Critique
*   **Future Readiness**: **High**. As LLMs shift from "Chatbots" to "Reasoning Agents" (System 2 thinking), they need structured memory. Graphs provide the "Map" that agents need to navigate complex information spaces.
*   **Critique**:
    *   **Cost & Latency**: Indexing is expensive. Building a graph with an LLM requires processing every token multiple times (extraction + summarization).
    *   **Static Nature**: Updating the graph when new documents arrive is harder than just adding a vector to a database. You often need to re-run community detection.
    *   **Complexity**: Requires maintaining a Graph DB (Neo4j) or NetworkX structures alongside a Vector DB.

## 6. Evolution & Problem Solving
*   **Problem Solved**: **"Connecting the Dots."**
    *   *Vector RAG*: Good for "Lookup" (Fact Retrieval).
    *   *GraphRAG*: Good for "Reasoning" (Pattern Recognition).
*   **Evolution**:
    1.  **Keyword Search**: TF-IDF (Matches exact words).
    2.  **Semantic Search (RAG)**: Embeddings (Matches meaning/context).
    3.  **Hybrid RAG**: Keyword + Semantic.
    4.  **GraphRAG**: Structured Relationships + Semantic Summaries.

## 7. Deep Dive: Architecture & Simulation

### 7.1 Architecture Diagram

```mermaid
flowchart TD
    subgraph Indexing ["Indexing Phase (Expensive, One-time)"]
        Docs[Raw Documents] --> Extract[LLM Entity Extraction]
        Extract --> Graph[Knowledge Graph (Nodes/Edges)]
        Graph --> Community[Community Detection (Leiden Alg)]
        Community --> Summarize[LLM Community Summarizer]
        Summarize --> Index[Community Summaries Index]
    end

    subgraph Querying ["Global Search Phase (Query Time)"]
        UserQ[User Query] --> Map[Map Step: Score Community Summaries]
        Index --> Map
        Map --> Reduce[Reduce Step: Aggregate Top Summaries]
        Reduce --> Answer[Final Global Answer]
    end

    style Indexing fill:#f9f,stroke:#333,stroke-width:2px
    style Querying fill:#bbf,stroke:#333,stroke-width:2px
```

### 7.2 Simulation Code
The following Python code simulates the **GraphRAG pipeline**. Since we cannot use a real LLM here, we use rule-based heuristics to mock "Entity Extraction" and "Summarization".

*Note: In production, the `extract_entities` and `generate_summary` functions would be calls to GPT-4.*

*(See `graphrag_simulation.py` in this folder for the executable code)*

```python
# Simplified Logic Preview
# 1. Documents -> Entities (Nodes)
# 2. Shared Entities -> Relationships (Edges)
# 3. Graph -> Communities (Clusters)
# 4. Communities -> Summaries
# 5. Query -> Aggregated Summary
```

## 8. References & Resources

*   **Microsoft Research Paper**: [From Local to Global: A GraphRAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130)
*   **Official GitHub Repository**: [microsoft/graphrag](https://github.com/microsoft/graphrag)
*   **Microsoft Research Blog**: [GraphRAG: Unlocking LLM discovery on private data](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-private-data/)
