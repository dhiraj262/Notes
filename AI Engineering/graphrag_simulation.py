import json
import random
import math
from typing import List, Dict, Set, Tuple, Any

# ==============================================================================
# GraphRAG Simulation
# ==============================================================================
# This script simulates the core mechanics of "GraphRAG" (Retrieval Augmented Generation with Graphs).
#
# CORE CONCEPTS SIMULATED:
# 1. Entity & Relation Extraction: (Mocked) Converting unstructured text into structured nodes/edges.
# 2. Graph Construction: Building an adjacency list representation of the knowledge.
# 3. Community Detection: Identifying clusters of closely related nodes (Leiden/Louvain analogue).
# 4. Community Summarization: Generating high-level insights for each cluster (Map step).
# 5. Global Search: Aggregating community summaries to answer broad questions (Reduce step).
#
# SCENARIO:
# A fictional post-mortem of a failed software launch "Project Apollo".
# - Data Chunks: Slack messages, logs, and emails.
# - Goal: Answer "Why did the launch fail?" (A global question requiring synthesis).
# ==============================================================================

class SimpleGraph:
    """A minimal Graph implementation using Adjacency Lists."""
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, List[str]] = {}

    def add_edge(self, u: str, v: str):
        self.nodes.add(u)
        self.nodes.add(v)
        if u not in self.edges: self.edges[u] = []
        if v not in self.edges: self.edges[v] = []
        if v not in self.edges[u]: self.edges[u].append(v)
        if u not in self.edges[v]: self.edges[v].append(u) # Undirected

    def get_connected_components(self) -> List[Set[str]]:
        """
        Simulates 'Community Detection'.
        In a real scenario, this would be Leiden or Louvain algorithm.
        Here, we find connected components to represent clusters.
        """
        visited = set()
        components = []

        for node in self.nodes:
            if node not in visited:
                component = set()
                stack = [node]
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr)
                        component.add(curr)
                        stack.extend([n for n in self.edges.get(curr, []) if n not in visited])
                components.append(component)
        return components

# ==============================================================================
# 1. THE DATASET (Unstructured Text)
# ==============================================================================
RAW_DOCUMENTS = [
    # Cluster 1: Database Issues
    "The PostgresDB is hitting max connection limits during peak hours.",
    "Latency on the primary database has increased by 400% since the migration.",
    "The connection pool settings in PostgresDB configuration are too low.",

    # Cluster 2: Frontend/User Issues
    "Users are reporting timeout errors on the checkout page.",
    "The checkout page spins forever when clicking 'Buy'.",
    "Customer support is flooded with tickets about failed transactions on the UI.",

    # Cluster 3: The "Bridge" (The Root Cause linking them)
    "The checkout service is opening a new DB connection for every single request instead of reusing them.",
    "Bad deployment #404 introduced a bug in the transaction handler."
]

# ==============================================================================
# 2. MOCK "LLM" EXTRACTION
# ==============================================================================
# In production, an LLM would read the text and output (Subject, Relation, Object).
# We simulate this with hardcoded extractions for the demo.
def mock_llm_extraction(docs: List[str]) -> List[Tuple[str, str, str]]:
    extracted_triples = []

    # Mapping rules to simulate LLM understanding
    extraction_rules = [
        ("PostgresDB", "has_issue", "max connection limits"),
        ("PostgresDB", "has_issue", "Latency"),
        ("connection pool", "is_part_of", "PostgresDB"),
        ("checkout page", "has_error", "timeout errors"),
        ("checkout page", "has_error", "spins forever"),
        ("Customer support", "receives", "tickets"),
        ("tickets", "relate_to", "checkout page"),
        ("checkout service", "causes", "new DB connection"),
        ("checkout service", "affects", "PostgresDB"), # The critical link!
        ("Bad deployment #404", "caused", "checkout service")
    ]

    # Return all for this simulation (in real life, it processes per doc)
    return extraction_rules

# ==============================================================================
# 3. MOCK "LLM" SUMMARIZATION
# ==============================================================================
def mock_llm_summarize_community(nodes: Set[str]) -> str:
    """
    Simulates the 'Map' step: summarizing a community of related nodes.
    """
    node_list = list(nodes)

    # Logic to return distinct summaries based on keywords present in the community nodes
    joined_nodes = " ".join(node_list).lower()

    if "deployment" in joined_nodes or "service" in joined_nodes:
        return "COMMUNITY C (Root Cause): A recent deployment (#404) broke the checkout service, causing it to mismanage database connections."
    elif "postgres" in joined_nodes or "latency" in joined_nodes:
        return "COMMUNITY A (Infrastructure): The Database layer is failing. PostgresDB is overwhelmed with connection spikes and high latency."
    elif "checkout" in joined_nodes and "customer" in joined_nodes:
        return "COMMUNITY B (User Experience): Users are unable to complete purchases. The checkout page is timing out, causing a support surge."
    else:
        return f"General Cluster containing: {', '.join(node_list)}"

# ==============================================================================
# 4. THE GRAPHRAG PIPELINE
# ==============================================================================
def run_graphrag_pipeline():
    print(f"--- 1. INGESTION: Processing {len(RAW_DOCUMENTS)} documents ---")

    # A. Indexing Phase
    graph = SimpleGraph()
    triples = mock_llm_extraction(RAW_DOCUMENTS)

    print("\n--- 2. EXTRACTION: Identifying Entities & Relations ---")
    for subj, rel, obj in triples:
        print(f"   Extracted: [{subj}] --{rel}--> [{obj}]")
        graph.add_edge(subj, obj)

    # B. Community Detection
    # In GraphRAG, this is hierarchical (Leiden algorithm). Here we use Connected Components.
    # Note: Our mock extraction makes a fully connected graph if we aren't careful.
    # To demonstrate 'Communities', let's assume the graph is slightly sparse or we force clusters.
    # For this demo, let's pretend the 'Link' was harder to find, but we'll just run component detection.
    # If the graph is fully connected (because of the "Bridge"), it will be 1 component.
    # To show the concept of communities, we will artificially split the graph for the 'Map' step
    # or just treat sub-clusters if our simple algo finds them.

    # *Self-Correction for Demo*: Simple Connected Components will merge everything if there is a bridge.
    # Let's verify what our graph looks like.
    # Postgres <-> connection pool
    # checkout service <-> Postgres (Bridge)
    # checkout service <-> Bad deployment
    # checkout page <-> checkout service (Implied? No, explicit link needed)

    # Let's just create Communities manually to simulate the *outcome* of the Leiden algorithm
    # which finds density clusters even in connected graphs.

    simulated_communities = [
        {"PostgresDB", "max connection limits", "Latency", "connection pool"},
        {"checkout page", "timeout errors", "spins forever", "Customer support", "tickets"},
        {"checkout service", "new DB connection", "Bad deployment #404", "PostgresDB", "checkout page"} # Overlap represents the bridge
    ]

    print("\n--- 3. CLUSTERING: Detecting Semantic Communities (Mocked Leiden) ---")
    community_summaries = []
    for i, comm in enumerate(simulated_communities):
        print(f"   Community {i+1}: {comm}")
        summary = mock_llm_summarize_community(comm)
        community_summaries.append(summary)
        print(f"   -> SUMMARY: {summary}")

    # C. Global Search (The "Reduce" Step)
    print("\n--- 4. QUERYING: Global Search ---")
    user_query = "What is the root cause of the system failure?"
    print(f"   User Query: '{user_query}'")

    # Baseline RAG approach (Vector Search comparison)
    print("\n   [VS] Baseline Vector Search would find:")
    print("      - 'System failure' -> No direct matches.")
    print("      - 'Cause' -> Maybe 'Bad deployment'.")
    print("      - It typically retrieves top-k chunks. It might miss the connection between 'Checkout' and 'DB' if they are far apart.")

    # GraphRAG approach
    print("\n   [VS] GraphRAG Global Search:")
    print("      Aggregating Community Summaries...")

    final_context = "\n".join([f"- {s}" for s in community_summaries])

    # Simulating the Final LLM generation based on the global context
    final_answer = (
        "Based on the global analysis of all clusters:\n"
        "The system failure is manifesting as User Timeouts (Community B) and Database Crashes (Community A). \n"
        "The CONNECTING factor is the 'Checkout Service' (Community C). \n"
        "ROOT CAUSE: Bad Deployment #404 introduced a bug in the Checkout Service that causes it to open new DB connections for every request, "
        "overwhelming the PostgresDB connection pool."
    )

    print("\n   === FINAL GRAPHRAG ANSWER ===")
    print(final_answer)

if __name__ == "__main__":
    run_graphrag_pipeline()
