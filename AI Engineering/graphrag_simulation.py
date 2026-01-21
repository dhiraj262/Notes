import json
import collections

class MockLLM:
    """
    Simulates an LLM for Entity Extraction and Summarization.
    In a real system, this would call OpenAI/Azure/DeepSeek.
    """

    def extract_triples(self, text_chunk):
        """
        Simulate extracting (Source, Relation, Target) triples from text.
        We use simple keyword matching for this demo.
        """
        triples = []
        text = text_chunk.lower()

        # Hardcoded logic to simulate "Smart" extraction for the demo scenario

        # Doc 1 & 2 Logic
        if "project titan" in text and "shadow corp" in text:
            triples.append(("Project Titan", "funded_by", "Shadow Corp"))

        if "project titan" in text and "quantum chip" in text:
            triples.append(("Project Titan", "develops", "Quantum Chip"))

        # Doc 3 Logic
        if "shadow corp" in text and "cayman islands" in text:
            triples.append(("Shadow Corp", "located_in", "Cayman Islands"))

        # Doc 4 Logic
        if "dr. aris" in text and "project titan" in text:
            triples.append(("Dr. Aris", "leads", "Project Titan"))

        if "dr. aris" in text and "university of ai" in text:
            triples.append(("Dr. Aris", "researcher_at", "University of AI"))

        return triples

    def summarize_community(self, entities, relations):
        """
        Simulates summarizing a community of nodes (entities).
        """
        # A real LLM would generate a natural language summary.
        return f"Community revolves around {', '.join(entities)}. Key relationships involve {', '.join(set([r[1] for r in relations]))}."

    def synthesize_answer(self, query, community_summaries):
        """
        Simulates the 'Reduce' step: Synthesizing an answer from global summaries.
        """
        # A real LLM would use the summaries to answer the specific query.
        print(f"\n[LLM Thinking] Analyzing {len(community_summaries)} community summaries against query: '{query}'...")

        # Check if we found the critical path in our summaries
        # We look for keywords in the *summaries* passed to this function
        full_context = " ".join(community_summaries).lower()

        if "funding" in query.lower() or "who is behind" in query.lower():
            if "shadow corp" in full_context and "cayman islands" in full_context and "project titan" in full_context:
                return "Based on the graph analysis: Project Titan is funded by 'Shadow Corp', which is located in the Cayman Islands. The graph connects these distinct entities."
            else:
                return "I could not find a complete connection in the graph data."

        return "I found some connections but need a more specific query."

class SimpleGraph:
    """
    A simple dependency-free Graph implementation.
    """
    def __init__(self):
        self.adj = collections.defaultdict(list) # Adjacency list
        self.edges = [] # List of (u, relation, v)

    def add_edge(self, u, relation, v):
        self.adj[u].append(v)
        self.adj[v].append(u) # Undirected for community detection
        self.edges.append((u, relation, v))

    def get_connected_components(self):
        """
        Simple community detection: Find connected components.
        Real GraphRAG uses Leiden algorithm for hierarchical clustering.
        """
        visited = set()
        communities = []

        for node in self.adj:
            if node not in visited:
                component = []
                stack = [node]
                visited.add(node)
                while stack:
                    curr = stack.pop()
                    component.append(curr)
                    for neighbor in self.adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            stack.append(neighbor)
                communities.append(component)
        return communities

class GraphRAGPipeline:
    def __init__(self):
        self.llm = MockLLM()
        self.graph = SimpleGraph()
        self.community_summaries = {} # Map ID -> Summary

    def index_documents(self, documents):
        print("--- Phase 1: Indexing (Extraction & Graph Building) ---")
        for i, doc in enumerate(documents):
            print(f"Processing Doc {i+1}...")
            triples = self.llm.extract_triples(doc)
            for u, r, v in triples:
                print(f"  -> Extracted: ({u}) -[{r}]-> ({v})")
                self.graph.add_edge(u, r, v)

        print("\n--- Phase 2: Community Detection & Summarization ---")
        communities = self.graph.get_connected_components()

        for i, comm in enumerate(communities):
            # Find edges internal to this community for context
            comm_edges = [e for e in self.graph.edges if e[0] in comm and e[2] in comm]
            summary = self.llm.summarize_community(comm, comm_edges)
            self.community_summaries[i] = summary
            print(f"Community {i} (Nodes: {len(comm)}): {summary}")

    def global_search(self, query):
        print(f"\n--- Phase 3: Global Search (Query: '{query}') ---")
        # In GraphRAG, we don't just look for "Project Titan".
        # We read ALL community summaries to get a holistic answer.

        answer = self.llm.synthesize_answer(query, self.community_summaries.values())
        print(f"\n>>> FINAL ANSWER:\n{answer}")

def main():
    # 1. The Dataset (Unstructured Text)
    # We tweak documents to ensure extraction logic fires and connects the graph.
    documents = [
        "Internal Memo: Project Titan is making progress on the Quantum Chip. Led by Dr. Aris.",
        "Confidential: The primary backer for Project Titan, Shadow Corp, has transferred the funds.",
        "Leak: Shadow Corp is a shell company solely located in the Cayman Islands to avoid taxes.",
        "Academic Profile: Dr. Aris is a leading researcher at the University of AI."
    ]

    rag = GraphRAGPipeline()
    rag.index_documents(documents)

    # 2. The "Global" Query
    # A question that requires connecting the dots across documents.
    query = "Who is behind the funding of Project Titan and where are they based?"
    rag.global_search(query)

if __name__ == "__main__":
    main()
