import collections
import re
import random

# --- Mock Infrastructure: Graph Structure ---

class SimpleGraph:
    """A minimal graph implementation to avoid external dependencies like networkx."""
    def __init__(self):
        self.nodes = set()
        self.edges = collections.defaultdict(set) # Adjacency list

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, source, target):
        self.add_node(source)
        self.add_node(target)
        self.edges[source].add(target)
        self.edges[target].add(source) # Undirected for this simulation

    def get_connected_components(self):
        """Finds connected components (simulating 'Communities')."""
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
                        stack.extend(self.edges[curr] - visited)
                components.append(list(component))
        return components

# --- Phase 1: Indexing (Extraction -> Graph -> Communities -> Summaries) ---

class GraphRAGIndexer:
    def __init__(self):
        self.graph = SimpleGraph()
        self.entity_docs = collections.defaultdict(list) # Map entity -> list of docs mentioning it
        self.community_summaries = {} # Map community_id -> summary text

    def ingest_documents(self, documents):
        print(f"📂 Ingesting {len(documents)} documents...")
        for i, doc in enumerate(documents):
            self._process_document(doc, doc_id=i)

        print(f"🕸️  Graph Built: {len(self.graph.nodes)} nodes")

    def _process_document(self, text, doc_id):
        """
        Mocks LLM Entity Extraction.
        Rule: Extracts Capitalized words as entities.
        Mocks Relationship Extraction.
        Rule: Connects all entities found in the same document.
        """
        # Simple regex to find proper nouns (Entities)
        entities = list(set(re.findall(r'\b[A-Z][a-zA-Z]+\b', text)))

        # Filter out common stop words that might be capitalized
        stop_words = {"The", "A", "An", "In", "On", "at", "To", "For", "Of", "And", "But", "So", "However", "Moreover", "Thus", "Therefore", "It", "He", "She", "They"}
        entities = [e for e in entities if e not in stop_words]

        if not entities:
            return

        # Add nodes and track source doc
        for entity in entities:
            self.graph.add_node(entity)
            self.entity_docs[entity].append(text)

        # Create edges (clique) between all entities in this doc
        # This simulates that they are "related" because they appear together
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                self.graph.add_edge(entities[i], entities[j])

    def build_communities(self):
        """
        Mocks Community Detection (e.g., Leiden algorithm).
        We use Connected Components for simplicity.
        """
        print("🔍 Detecting Communities...")
        components = self.graph.get_connected_components()

        for i, component in enumerate(components):
            # In a real system, communities are hierarchical and overlapping.
            # Here, we just give them IDs.
            print(f"   Community {i}: {', '.join(component)}")
            self._summarize_community(i, component)

    def _summarize_community(self, community_id, entities):
        """
        Mocks LLM Summarization.
        Aggregates context from documents linked to these entities.
        """
        # Gather all text related to this community
        related_texts = []
        for entity in entities:
            related_texts.extend(self.entity_docs[entity])

        # Unique texts only
        related_texts = list(set(related_texts))

        # "LLM" Summary Generation (Mock)
        summary = f"Community {community_id} represents a cluster involving {', '.join(entities)}. "
        summary += f"Key topics discussed: {len(related_texts)} source documents linked. "
        summary += "Narrative: Entities in this group are frequently co-mentioned, suggesting a strong thematic relationship."

        self.community_summaries[community_id] = summary
        print(f"   📝 Generated Summary for Community {community_id}")

# --- Phase 2: Querying (Global Search) ---

class GraphRAGQueryEngine:
    def __init__(self, indexer):
        self.indexer = indexer

    def global_search(self, query):
        """
        Performs Global Search by aggregating Community Summaries.
        Standard RAG would just look for chunks matching the query keywords.
        GraphRAG looks at the 'Big Picture' summaries.
        """
        print(f"\n❓ User Query: '{query}'")
        print("🌍 Performing Global Graph Search...")

        # 1. Map: Score each community summary (Mock scoring)
        # In reality, we'd use an LLM to rate if the summary answers the query.
        relevant_summaries = []
        print("   ... Analyzing Community Summaries")
        for c_id, summary in self.indexer.community_summaries.items():
            # Mock Relevance: Always include for this demo, or random
            # For a real feel, let's say we pick all of them to synthesize a global answer
            relevant_summaries.append(summary)

        # 2. Reduce: Synthesize the final answer
        print("   ... Synthesizing Answer from Community Contexts")
        final_answer = self._synthesize_answer(query, relevant_summaries)
        return final_answer

    def _synthesize_answer(self, query, summaries):
        # Mock LLM generation
        answer = f"Based on the global analysis of the provided documents, here is the answer to '{query}':\n\n"

        answer += "The analysis identified several key thematic clusters:\n"
        for i, summary in enumerate(summaries):
            answer += f"- {summary}\n"

        answer += "\nConclusion: The graph structure reveals these distinct groups are interconnected through shared documents, providing a holistic view that individual retrieval might miss."
        return answer

# --- Simulation Execution ---

def main():
    # 1. Dataset: A set of disjoint-looking texts that form a hidden story
    documents = [
        "Project Alpha is led by Alice. It focuses on Quantum Computing.",
        "Alice meets with Bob regularly to discuss security protocols.",
        "Bob works for CyberCorp, a company investigating Quantum encryption.",
        "CyberCorp recently acquired DataFlow, a startup in Silicon Valley.",
        "Charlie is the CEO of DataFlow. He specializes in AI optimization.",
        "Project Beta is a rival initiative run by Dave.",
        "Dave was seen arguing with Charlie about market share.",
    ]

    # 2. Initialize Indexer
    indexer = GraphRAGIndexer()

    # 3. Build Index (Ingest -> Graph -> Communities -> Summaries)
    indexer.ingest_documents(documents)
    indexer.build_communities()

    # 4. Initialize Query Engine
    engine = GraphRAGQueryEngine(indexer)

    # 5. Execute Global Query
    # A standard RAG might just find docs with "Alice" or "Charlie".
    # GraphRAG can answer "How are the projects and companies connected?"
    response = engine.global_search("What is the relationship landscape between the people and companies?")

    print("\n" + "="*50)
    print("FINAL RESPONSE")
    print("="*50)
    print(response)

if __name__ == "__main__":
    main()
