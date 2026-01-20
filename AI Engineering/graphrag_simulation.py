import collections
import random
import time
from typing import List, Dict, Tuple, Set

# --- Mock LLM & Data Structures ---

class MockLLM:
    """Simulates an LLM for entity extraction and summarization."""

    def extract_entities(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Simulates extracting (Source, Relation, Target) triples from text.
        In a real scenario, this uses a prompt like 'Extract all entities and relationships...'.
        """
        # Hardcoded extraction for the simulation example
        if "SpaceX" in text:
            return [
                ("SpaceX", "founded_by", "Elon Musk"),
                ("SpaceX", "develops", "Starship"),
                ("Elon Musk", "ceo_of", "Tesla"),
                ("Starship", "designed_for", "Mars Colonization")
            ]
        elif "NASA" in text:
            return [
                ("NASA", "partners_with", "SpaceX"),
                ("NASA", "operates", "ISS"),
                ("ISS", "located_in", "Low Earth Orbit")
            ]
        return []

    def summarize_community(self, entities: List[str], relations: List[Tuple[str, str, str]]) -> str:
        """
        Simulates summarizing a cluster of related entities.
        """
        if not entities:
            return "Empty Community"
        # Simple template-based summary
        main_entities = ", ".join(entities[:3])
        rel_example = relations[0][1] if relations else "various links"
        return f"Community focused on {main_entities}. Key relationships involve {len(relations)} connections including {rel_example}."

    def answer_global_query(self, community_summaries: List[str], query: str) -> str:
        """
        Synthesizes an answer from community summaries.
        """
        valid_summaries = [s for s in community_summaries if s != "Empty Community"]
        return f"Based on the analysis of {len(valid_summaries)} relevant communities: The dataset highlights a collaboration between private and public sectors. {valid_summaries[0]} connects with {valid_summaries[1] if len(valid_summaries) > 1 else 'other entities'} to enable space missions."

# --- GraphRAG Engine Components ---

class GraphRAGEngine:
    def __init__(self):
        self.llm = MockLLM()
        self.graph = collections.defaultdict(list) # Adjacency list: node -> [(relation, target)]
        self.edges = [] # List of (source, relation, target)
        self.communities = [] # List of lists of nodes

    def index_documents(self, documents: List[str]):
        """Step 1: Element Extraction & Graph Construction"""
        print("\n--- Step 1: Indexing & Graph Construction ---")
        for i, doc in enumerate(documents):
            print(f"Processing Document {i+1}...")
            triples = self.llm.extract_entities(doc)
            for source, rel, target in triples:
                # Add to adjacency list (undirected for community detection usually, but here we keep directed for storage)
                self.graph[source].append((rel, target))
                # Tracking edges
                self.edges.append((source, rel, target))
                # Add nodes to graph keys if not present
                if target not in self.graph:
                    self.graph[target] = []

                print(f"  -> Extracted: ({source}) --[{rel}]--> ({target})")

        print(f"Graph built with {len(self.graph)} nodes and {len(self.edges)} edges.")

    def detect_communities(self):
        """Step 2: Community Detection (Simulating Leiden Algorithm)"""
        print("\n--- Step 2: Community Detection (Hierarchical) ---")
        # In GraphRAG, this uses the Leiden algorithm to find dense subgraphs.
        # We will manually cluster based on our known entities for the simulation.

        nodes = list(self.graph.keys())
        # Community 1: Private Space (SpaceX, Musk, etc.)
        c1 = [n for n in nodes if n in ["SpaceX", "Elon Musk", "Tesla", "Starship", "Mars Colonization"]]
        # Community 2: Public Space (NASA, ISS, etc.)
        c2 = [n for n in nodes if n in ["NASA", "ISS", "Low Earth Orbit"]]

        self.communities = [c1, c2]

        for i, comm in enumerate(self.communities):
            print(f"Community {i}: {comm}")

    def generate_community_summaries(self):
        """Step 3: Community Summarization"""
        print("\n--- Step 3: Community Summarization ---")
        self.community_summaries = []
        for i, comm in enumerate(self.communities):
            if not comm:
                continue
            # Get internal edges (where both source and target are in the community)
            comm_edges = [e for e in self.edges if e[0] in comm and e[2] in comm]
            summary = self.llm.summarize_community(comm, comm_edges)
            self.community_summaries.append(summary)
            print(f"Summary {i}: {summary}")

    def global_query(self, query: str):
        """Step 4: Global Query (Map-Reduce)"""
        print(f"\n--- Step 4: Global Query: '{query}' ---")
        # "Map" phase was the summarization.
        # "Reduce" phase is synthesizing the answer from the summaries.
        final_answer = self.llm.answer_global_query(self.community_summaries, query)
        print(f"FINAL ANSWER:\n{final_answer}")

# --- Simulation Execution ---

def main():
    docs = [
        "SpaceX was founded by Elon Musk to revolutionize space technology. SpaceX develops Starship for Mars Colonization. Elon Musk is also the CEO of Tesla.",
        "NASA partners with SpaceX for various missions. NASA operates the ISS which is located in Low Earth Orbit."
    ]

    rag = GraphRAGEngine()

    # 1. Build the graph
    rag.index_documents(docs)

    # 2. Find communities
    rag.detect_communities()

    # 3. Summarize communities
    rag.generate_community_summaries()

    # 4. Ask a global question
    rag.global_query("What are the major players in space exploration mentioned?")

if __name__ == "__main__":
    main()
