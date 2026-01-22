import hashlib
import json
import random
from collections import defaultdict

# --- Mock Data ---
DOCUMENTS = [
    "Project Apollo was led by Sarah Connor. It aimed to develop a new solar battery.",
    "The solar battery prototype, named SunCell, faced overheating issues in Q3.",
    "Sarah Connor appointed John Smith to fix the SunCell overheating problem.",
    "John Smith previously worked on Project Hades, which failed due to funding.",
    "Project Hades was a competitor to Project Apollo in the energy sector."
]

# --- 1. Indexing Phase: Entity Extraction ---
# In a real system, an LLM would do this. Here we use a deterministic mock.
def mock_extract_entities_and_relations(text):
    """
    Extracts entities and relations based on simple keywords for simulation.
    """
    entities = set()
    relations = []

    # Simple rule-based extraction for the demo
    keywords = ["Project Apollo", "Sarah Connor", "SunCell", "John Smith", "Project Hades", "Solar Battery"]

    # Check for keywords in text (case insensitive mostly, but here simple string match)
    found = [k for k in keywords if k in text]
    for entity in found:
        entities.add(entity)

    # Create simple relations if multiple entities appear in the same text
    if len(found) > 1:
        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                relations.append((found[i], "related_to", found[j]))

    return list(entities), relations

# --- 2. Graph Construction ---
class SimpleGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, u, v, relation):
        self.add_node(u)
        self.add_node(v)
        self.edges[u].append((v, relation))
        self.edges[v].append((u, relation)) # Undirected for community detection

# --- 3. Community Detection (Leiden/Louvain Mock) ---
def mock_community_detection(graph):
    """
    A simplified community detection.
    In reality, GraphRAG uses Leiden. Here, we'll just group connected components
    or use a simple greedy grouping for demonstration.
    """
    communities = {} # community_id -> list of nodes
    visited = set()
    community_id = 0

    sorted_nodes = sorted(list(graph.nodes))

    for node in sorted_nodes:
        if node not in visited:
            # Start a new community (BFS)
            queue = [node]
            visited.add(node)
            current_comm = []

            while queue:
                curr = queue.pop(0)
                current_comm.append(curr)

                # Simulate traversing connected components
                for neighbor, _ in graph.edges[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            communities[community_id] = current_comm
            community_id += 1

    return communities

# --- 4. Community Summarization ---
def generate_community_summaries(communities, graph):
    """
    Simulates generating a summary for each community.
    """
    summaries = {}
    for cid, nodes in communities.items():
        # In reality, we'd feed node descriptions + edges to an LLM.
        # Here we construct a template string.
        relations = []
        seen_rels = set()
        for u in nodes:
            for v, rel in graph.edges[u]:
                if v in nodes:
                    # Sort to avoid duplicates in set key
                    pair = tuple(sorted((u, v)))
                    if pair not in seen_rels:
                        relations.append(f"{u} {rel} {v}")
                        seen_rels.add(pair)

        summary = f"Community {cid} revolves around {', '.join(nodes)}. Key relationships: {'; '.join(relations)}."
        summaries[cid] = summary
    return summaries

# --- 5. Query Phase ---

def naive_rag_query(query, docs):
    """
    Simulates Naive RAG: retrieve docs containing keywords.
    """
    print(f"\n--- Naive RAG Query: '{query}' ---")
    retrieved = []
    query_words = query.lower().split()
    for doc in docs:
        if any(word in doc.lower() for word in query_words if len(word) > 3): # Simple filter
            retrieved.append(doc)

    if not retrieved:
        return "No relevant documents found."

    # Simulate LLM synthesis
    context = " | ".join(retrieved)
    return f"Based on {len(retrieved)} retrieved docs. Context snippet: {context[:150]}..."

def graph_rag_query(query, community_summaries):
    """
    Simulates Global GraphRAG Query: Use community summaries to answer.
    """
    print(f"\n--- GraphRAG Global Query: '{query}' ---")

    # 1. Map: Score communities based on query relevance
    relevant_summaries = []
    query_words = query.lower().split()

    for cid, summary in community_summaries.items():
        # Simple keyword overlap scoring
        score = sum(1 for word in query_words if word in summary.lower())
        if score > 0:
            relevant_summaries.append(summary)

    if not relevant_summaries:
        # If no direct keyword hit in summaries, GraphRAG often performs a global map-reduce
        # over all top-level communities to synthesized an answer (Global Search).
        print("(No direct keyword hit in summaries, performing Global Map-Reduce over all communities)")
        relevant_summaries = list(community_summaries.values())

    # 2. Reduce: Synthesize answer
    final_context = "\n".join([f"- {s}" for s in relevant_summaries])
    return f"GraphRAG Answer derived from Community Summaries:\n{final_context}"


# --- Main Simulation ---
def run_simulation():
    print("=== GraphRAG Simulation Pipeline ===\n")

    # 1. Indexing
    print("1. [Indexing] Processing Documents...")
    graph = SimpleGraph()
    all_entities = set()

    for doc in DOCUMENTS:
        entities, relations = mock_extract_entities_and_relations(doc)
        for e in entities:
            all_entities.add(e)
        for u, rel, v in relations:
            graph.add_edge(u, v, rel)

    print(f"   > Extracted {len(all_entities)} entities and {sum(len(v) for v in graph.edges.values())//2} relationships.")

    # 2. Community Detection
    print("2. [Graph] Detecting Communities...")
    communities = mock_community_detection(graph)
    for cid, nodes in communities.items():
        print(f"   > Community {cid}: {nodes}")

    # 3. Summarization
    print("3. [Summarization] Generating Community Summaries...")
    summaries = generate_community_summaries(communities, graph)
    for cid, s in summaries.items():
        print(f"   > Summary {cid}: {s}")

    # 4. Comparison
    # A query that requires bridging gaps.
    # Naive RAG might find Sarah Connor docs and Project Hades docs separately,
    # but might not easily synthesize the link without a massive context window or lucky retrieval.
    # GraphRAG has the "path" encoded in the community summary.
    query = "How is Sarah Connor connected to Project Hades?"

    # Naive RAG
    naive_ans = naive_rag_query(query, DOCUMENTS)
    print(f"Result: {naive_ans}")

    # Graph RAG
    graph_ans = graph_rag_query(query, summaries)
    print(f"Result: {graph_ans}")

    print("\n=== Simulation Complete ===")

if __name__ == "__main__":
    run_simulation()
