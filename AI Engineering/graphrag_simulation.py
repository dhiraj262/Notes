import networkx as nx
import random
import time
from collections import defaultdict

class SimpleGraphRAG:
    """
    A simplified simulation of a GraphRAG system.

    It demonstrates the core architectural pattern:
    1. Indexing: Extracting Entities/Relations from text (Mocked).
    2. Graph Construction: Building a NetworkX graph.
    3. Community Detection: Grouping nodes into communities.
    4. Summarization: Creating summaries for communities (Mocked).
    5. Querying: Global Search via Map-Reduce over communities.
    """

    def __init__(self):
        self.graph = nx.Graph()
        self.communities = {} # id -> list of nodes
        self.community_summaries = {} # id -> text summary
        self.chunks = []

    def log(self, message):
        print(f"[GraphRAG System] {message}")

    # --- 1. Indexing Phase ---

    def index_documents(self, documents):
        self.log("Starting Indexing Phase...")

        # Step 1: Chunking (Simplified split by sentence)
        chunks = []
        for doc in documents:
            chunks.extend(doc.split(". "))
        self.chunks = chunks
        self.log(f"Process: Split documents into {len(chunks)} chunks.")

        # Step 2: Entity & Relation Extraction (Mocked LLM)
        # In a real system, an LLM would parse the text to find entities.
        # Here we simulate this with a mock function based on keywords.
        self.log("Process: Extracting Entities and Relationships (Simulating LLM)...")
        for chunk in chunks:
            self._mock_extract_and_add_to_graph(chunk)

        self.log(f"Graph Built: {self.graph.number_of_nodes()} Nodes, {self.graph.number_of_edges()} Edges.")

        # Step 3: Community Detection (Simulating Leiden/Louvain)
        self._detect_communities()

        # Step 4: Community Summarization (Simulating LLM)
        self._summarize_communities()

        self.log("Indexing Complete.\n")

    def _mock_extract_and_add_to_graph(self, text):
        """
        Simulates an LLM extracting (Subject, Relation, Object) triples.
        We use hardcoded logic for the demo story to ensure a connected graph.
        """
        # A simple mock extraction based on the provided story context
        entities = [
            "Alice", "Bob", "Project Apollo", "CyberCorp", "Eve",
            "Server Room", "Encrypted Drive", "HR Dept", "CEO", "Secret Protocol"
        ]

        text_lower = text.lower()
        found_entities = [e for e in entities if e.lower() in text_lower]

        # Add nodes
        for entity in found_entities:
            self.graph.add_node(entity, type="Entity")

        # Add edges (connect entities found in the same chunk)
        import itertools
        for e1, e2 in itertools.combinations(found_entities, 2):
            self.graph.add_edge(e1, e2, source_text=text)

    def _detect_communities(self):
        """
        Simulates community detection (e.g., Leiden algorithm).
        We use a simple connected components or just mock clustering for the demo.
        """
        self.log("Process: Detecting Communities in the Knowledge Graph...")

        # For simulation, we'll just use connected components or a mock partition
        # If the graph is fully connected, we might just split it arbitrarily to show the concept

        # Let's use simple modularity-based community detection if available, or fallback
        try:
            communities = list(nx.community.greedy_modularity_communities(self.graph))
        except:
            # Fallback for simple demo if dependencies miss or graph too small
            communities = [list(self.graph.nodes())]

        for i, comm in enumerate(communities):
            self.communities[i] = list(comm)
            self.log(f"  > Community {i}: {list(comm)}")

    def _summarize_communities(self):
        """
        Simulates the LLM generating a summary for each community.
        This is crucial for 'Global Search'.
        """
        self.log("Process: Generating Summaries for each Community (Simulating LLM)...")

        for cid, nodes in self.communities.items():
            # Mock summary generation based on nodes present
            summary = f"Community {cid} focuses on interaction between {', '.join(nodes[:3])}..."
            if "Alice" in nodes and "Bob" in nodes:
                summary += " It involves internal collaboration and potential security risks."
            elif "CyberCorp" in nodes:
                summary += " It concerns external corporate entities and high-level strategy."

            self.community_summaries[cid] = summary

    # --- 2. Querying Phase ---

    def global_search(self, query):
        """
        Demonstrates the 'Global Search' capability of GraphRAG.
        It does NOT look for specific chunks. It looks at Community Summaries.
        """
        self.log(f"Executing Global Search for: '{query}'")
        self.log("Strategy: Map-Reduce over Community Summaries.")

        # MAP Phase: Rate relevance of each community summary
        relevant_summaries = []
        for cid, summary in self.community_summaries.items():
            # Mock scoring (Simulating LLM evaluation)
            score = 0
            if "risk" in query.lower() or "security" in query.lower():
                if "security" in summary.lower() or "risk" in summary.lower() or "Alice" in summary:
                    score = 0.9

            if score > 0.5:
                relevant_summaries.append(summary)
                self.log(f"  > Used Community {cid} Summary (Score {score})")

        # REDUCE Phase: Synthesize answer
        if not relevant_summaries:
            return "No relevant patterns found in the global context."

        final_answer = "Global Analysis reveals:\n" + "\n".join([f"- {s}" for s in relevant_summaries])
        return final_answer

    def local_search(self, query):
        """
        Standard Entity traversal.
        """
        self.log(f"Executing Local Search for: '{query}'")
        # Simple keyword match
        start_node = None
        for node in self.graph.nodes():
            if node.lower() in query.lower():
                start_node = node
                break

        if not start_node:
            return "Entity not found in graph."

        neighbors = list(self.graph.neighbors(start_node))
        return f"Found '{start_node}'. It is directly connected to: {', '.join(neighbors)}."

# --- Simulation Execution ---

if __name__ == "__main__":
    print("=== Starting GraphRAG Simulation ===\n")

    # Sample Data: A corporate thriller story snippet
    documents = [
        "Alice works in the Server Room at CyberCorp. She has access to the Encrypted Drive.",
        "Bob from HR Dept met with Alice to discuss a Secret Protocol.",
        "The CEO of CyberCorp announced a new partnership with Project Apollo.",
        "Eve was seen near the Server Room late at night. The Encrypted Drive went missing the next day.",
        "Project Apollo requires the Secret Protocol to function correctly."
    ]

    rag = SimpleGraphRAG()

    # 1. Build the Index
    rag.index_documents(documents)

    # 2. Local Query (Specific Fact)
    print("--- Test 1: Local Search (Specific Fact) ---")
    print(f"Answer: {rag.local_search('Who is connected to Alice?')}\n")

    # 3. Global Query (High-Level Theme)
    print("--- Test 2: Global Search (Thematic Reasoning) ---")
    query = "What are the security risks involving internal staff?"
    print(f"Answer: {rag.global_search(query)}\n")

    print("=== Simulation Complete ===")
