import re
import collections
import itertools

class GraphRAGSimulator:
    """
    A self-contained simulation of the GraphRAG pipeline using standard Python libraries.
    It demonstrates:
    1. Entity Extraction (Mocking LLM)
    2. Graph Construction (NetworkX-style adjacency list)
    3. Community Detection (Simplified Connected Components)
    4. Community Summarization (Map Step)
    5. Global Answer Generation (Reduce Step)
    """
    def __init__(self):
        self.graph = collections.defaultdict(set) # Adjacency list: node -> set(neighbors)
        self.entities = set()
        self.communities = []
        self.community_summaries = {}

    def ingest_documents(self, documents):
        """
        Simulate the indexing phase: Chunking -> Extraction -> Graph Building
        """
        print("--- Phase 1: Ingestion & Extraction ---")
        for i, doc in enumerate(documents):
            print(f"Processing Document {i+1}: '{doc}'")
            # 1. Chunking (Simplified: Treat whole doc as one chunk)
            chunks = [doc]

            # 2. Extraction (Mock LLM)
            for chunk in chunks:
                extracted_entities = self._mock_llm_extract_entities(chunk)
                if extracted_entities:
                    print(f"  > Extracted Entities: {extracted_entities}")
                    self._update_graph(extracted_entities)
                else:
                    print("  > No entities found.")

    def _mock_llm_extract_entities(self, text):
        """
        Heuristic to mock LLM extraction: Extract Capitalized Words (Entities).
        In a real system, an LLM would extract (Subject, Predicate, Object).
        """
        # Regex to find capitalized words or CamelCase that are likely names/proper nouns
        # Matches words starting with Capital and containing letters.
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        # Filter out some common stop words if they appear capitalized at start of sentence (Mocking)
        stop_words = {"The", "A", "An", "In", "On", "Has", "Is", "Are", "And"}
        return list(set([w for w in words if w not in stop_words]))

    def _update_graph(self, entities):
        """
        Build the graph:
        - Nodes: Entities
        - Edges: Co-occurrence in the same text chunk
        """
        # Add nodes
        for entity in entities:
            self.entities.add(entity)

        # Add edges (Clique expansion for entities in same chunk)
        # If A, B, C are in chunk, we add edges (A,B), (B,C), (A,C)
        for u, v in itertools.combinations(entities, 2):
            self.graph[u].add(v)
            self.graph[v].add(u) # Undirected graph

    def detect_communities(self):
        """
        Simulate Community Detection (e.g., Leiden Algorithm).
        Here we use 'Connected Components' as a proxy for dense communities.
        """
        print("\n--- Phase 2: Community Detection (Simulating Leiden) ---")
        visited = set()
        community_id = 0

        for entity in self.entities:
            if entity not in visited:
                # BFS to find component
                community = []
                queue = [entity]
                visited.add(entity)
                while queue:
                    node = queue.pop(0)
                    community.append(node)
                    for neighbor in self.graph[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                self.communities.append(community)
                print(f"  Community {community_id} detected: {community}")
                community_id += 1

    def generate_community_summaries(self):
        """
        Simulate the Map Step: Generate a summary for each community.
        """
        print("\n--- Phase 3: Community Summarization (Map Step) ---")
        for i, community in enumerate(self.communities):
            # Mock LLM Summarization: Just listing the entities and relationships
            # In real GraphRAG, the LLM reads all chunks associated with these entities.
            summary = f"Community {i} revolves around {', '.join(community)}. " \
                      f"They are linked through shared contexts in the documents."
            self.community_summaries[i] = summary
            print(f"  Summary {i}: {summary}")

    def global_query(self, query):
        """
        Simulate the Reduce Step: Answer a global question using community summaries.
        """
        print(f"\n--- Phase 4: Global Query Processing: '{query}' ---")

        # MAP: The system "reads" all community summaries (or filters by relevance)
        # For a global summary query, we read all of them.
        print("  > Reading community summaries...")
        partial_responses = list(self.community_summaries.values())

        # REDUCE: Aggregate into final answer
        print("  > Synthesizing final answer...")
        final_answer = self._mock_llm_reduce(partial_responses)
        return final_answer

    def _mock_llm_reduce(self, summaries):
        """
        Mock LLM aggregation of summaries.
        """
        combined = " ".join(summaries)
        return (
            f"**GLOBAL INSIGHT GENERATED**\n"
            f"Based on the analysis of {len(self.communities)} distinct communities in the data:\n"
            f"{combined}\n"
            f"(Note: This answer was derived by traversing the knowledge graph structure, "
            f"not just keyword matching.)"
        )

def main():
    # Sample Dataset: A small narrative with hidden connections
    docs = [
        "Alice and Bob are working on the TopSecret project at TechCorp.",
        "TechCorp has just signed a deal with CyberDyne Systems.",
        "Eve is a lead engineer at CyberDyne Systems.",
        "Bob has been seen having lunch with Eve frequently.",
        "Charlie handles security for TopSecret and suspects a leak."
    ]

    rag = GraphRAGSimulator()
    rag.ingest_documents(docs)
    rag.detect_communities()
    rag.generate_community_summaries()

    # A Global Query that requires connecting TechCorp -> CyberDyne -> Eve -> Bob -> TopSecret
    answer = rag.global_query("What are the potential security risks involving external collaborations?")
    print(f"\n{answer}")

if __name__ == "__main__":
    main()
