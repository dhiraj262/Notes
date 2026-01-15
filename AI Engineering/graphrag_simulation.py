import re
import collections

class SimpleGraphRAG:
    """
    A simplified simulation of the GraphRAG pipeline using standard Python.
    Demonstrates:
    1. Entity Extraction (Mocked)
    2. Graph Construction
    3. Community Detection (Connected Components)
    4. Community Summarization
    5. Global Search
    """

    def __init__(self):
        self.graph = collections.defaultdict(list) # Adjacency list
        self.entities = set()
        self.edges = []
        self.communities = []
        self.community_summaries = {}

    def index_documents(self, documents):
        """
        Simulates the Indexing Phase:
        Text -> (LLM Extraction) -> Entities/Relations -> Graph
        """
        print(f"--- 1. Indexing {len(documents)} Documents ---")
        for doc in documents:
            self._mock_llm_extraction(doc)

        print(f"Extracted {len(self.entities)} entities and {len(self.edges)} relationships.")

        # Build the graph structure
        self._build_graph()

        # Detect communities (Simulating Leiden Algorithm)
        self._detect_communities()

        # Generate summaries for communities
        self._generate_community_summaries()

    def _mock_llm_extraction(self, text):
        """
        Simulates an LLM extracting entities and relationships.
        For this demo, we use a simple heuristic:
        - Entities: Capitalized words (ignoring starting words if possible, but keeping it simple).
        - Relations: If two entities appear in the same sentence, they are related.
        """
        sentences = text.split('.')
        for sentence in sentences:
            # Find capitalized words as "Entities"
            # (Simple regex for demo purposes)
            found_entities = list(set(re.findall(r'\b[A-Z][a-zA-Z]*\b', sentence)))

            # Filter out common stop words if they accidentally get capitalized
            stop_words = {"The", "A", "An", "In", "On", "It", "He", "She", "They"}
            found_entities = [e for e in found_entities if e not in stop_words and len(e) > 1]

            # Add to set
            for entity in found_entities:
                self.entities.add(entity)

            # Create edges (relationships) between all pairs in the sentence
            for i in range(len(found_entities)):
                for j in range(i + 1, len(found_entities)):
                    entity_a = found_entities[i]
                    entity_b = found_entities[j]
                    self.edges.append((entity_a, entity_b))
                    # print(f"  [Extraction] Found relation: {entity_a} <--> {entity_b}")

    def _build_graph(self):
        """
        Builds the adjacency list from extracted edges.
        """
        for u, v in self.edges:
            self.graph[u].append(v)
            self.graph[v].append(u) # Undirected graph

    def _detect_communities(self):
        """
        Simulates Community Detection (e.g., Leiden/Louvain).
        Here we just use 'Connected Components' for simplicity.
        """
        print("\n--- 2. Detecting Communities (Graph Clustering) ---")
        visited = set()
        for entity in self.entities:
            if entity not in visited:
                component = []
                stack = [entity]
                visited.add(entity)
                while stack:
                    node = stack.pop()
                    component.append(node)
                    for neighbor in self.graph[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            stack.append(neighbor)
                self.communities.append(component)

        print(f"Detected {len(self.communities)} distinct communities (clusters).")
        for i, comm in enumerate(self.communities):
            print(f"  Community {i}: {comm}")

    def _generate_community_summaries(self):
        """
        Simulates generating a summary for each community.
        In real GraphRAG, an LLM reads all text associated with these nodes.
        Here, we just synthesize a summary string.
        """
        print("\n--- 3. Generating Community Summaries ---")
        for i, comm in enumerate(self.communities):
            # Simulation: Create a 'theme' based on the nodes
            summary = f"This community revolves around {', '.join(comm[:3])}..."
            if "Bug" in comm or "Fix" in comm:
                summary += " It involves technical issues and resolutions."
            elif "CEO" in comm or "Money" in comm:
                summary += " It involves corporate leadership and finance."

            self.community_summaries[i] = summary
            print(f"  Summary {i}: {summary}")

    def global_search(self, query):
        """
        Simulates a 'Global Search' query.
        Instead of searching for keywords, it aggregates community summaries.
        """
        print(f"\n--- 4. Global Search Query: '{query}' ---")
        print("GraphRAG Strategy: Aggregating Community Summaries...")

        # In real GraphRAG, we would score communities by relevance,
        # but for Global Search, we often read all top-level summaries (Map-Reduce).

        final_answer_context = []
        for i, summary in self.community_summaries.items():
            final_answer_context.append(f"- Community {i}: {summary}")

        combined_context = "\n".join(final_answer_context)

        print("\n[Simulating LLM Final Answer Generation based on this context]:")
        print("-" * 40)
        print(combined_context)
        print("-" * 40)

        # Mocking the final LLM output
        print("\n>> GENERATED ANSWER:")
        print(f"To answer '{query}', we look at the structural communities:")
        print("The dataset contains distinct groups. One focuses on leadership/finance (Community 0), "
              "while another focuses on technical operations (Community 1). "
              "Unlike naive RAG, which might just find the word 'finance', "
              "GraphRAG sees the whole interconnected cluster of actors.")

# ==========================================
# RUN THE SIMULATION
# ==========================================

if __name__ == "__main__":
    # Sample Dataset: A fictional chaotic startup story
    documents = [
        "Alice is the CEO of FutureTech. She engaged in a meeting with Bob, the CFO, about Money.",
        "Bob is worried about the Budget. The Budget is shrinking due to low Sales.",
        "Charlie is a Developer at FutureTech. He found a critical Bug in the System.",
        "The Bug caused a System crash. Charlie asked Dave for help with the Fix.",
        "Eve is a competitor from EvilCorp. Eve is trying to steal the Algorithm from Alice."
    ]

    rag = SimpleGraphRAG()
    rag.index_documents(documents)

    # Perform a Global Query
    rag.global_search("What is the overall situation at FutureTech?")
