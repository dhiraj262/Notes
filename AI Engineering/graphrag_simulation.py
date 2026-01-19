import collections
import re
import random

class SimpleGraph:
    """
    A minimal in-memory graph implementation to avoid external dependencies like networkx.
    """
    def __init__(self):
        self.adj = collections.defaultdict(list)
        self.nodes = set()

    def add_edge(self, u, v):
        self.nodes.add(u)
        self.nodes.add(v)
        self.adj[u].append(v)
        self.adj[v].append(u) # Undirected

    def get_connected_components(self):
        """
        Simple community detection: finding connected components.
        In real GraphRAG, this would be the Leiden algorithm.
        """
        visited = set()
        components = []

        for node in self.nodes:
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
                components.append(component)
        return components

class MockLLM:
    """
    Simulates LLM calls for Entity Extraction and Summarization.
    """
    def extract_entities(self, text):
        """
        Simulate extracting entities and relationships.
        In a real scenario, this uses an LLM prompt.
        Here we use simple rule-based matching for the demo scenario.
        """
        entities = []
        relationships = []

        # Scenario: Project Status Reports
        # Entities: Person (Alice, Bob), Project (Alpha, Beta), Risk (Delay, Budget)

        # Simple extraction rules for the demo
        words = text.replace('.', '').split()

        # Detect people and projects based on known keywords (Simulating NER)
        known_entities = {
            "Alice": "Person", "Bob": "Person", "Charlie": "Person",
            "Project Alpha": "Project", "Project Beta": "Project",
            "Server Crash": "Risk", "Budget Cut": "Risk"
        }

        found = []
        for phrase, type_ in known_entities.items():
            if phrase in text:
                found.append(phrase)

        # Create relationships if multiple entities found in same text chunk
        if len(found) > 1:
            for i in range(len(found)):
                for j in range(i+1, len(found)):
                    relationships.append((found[i], found[j]))

        return found, relationships

    def summarize_community(self, entities):
        """
        Simulate summarizing a community of related entities.
        """
        # Dynamic template based on content
        summary = f"Community covering {', '.join(entities)}."

        if "Project Alpha" in entities and "Server Crash" in entities:
            summary += " Major focus: Project Alpha is suffering from technical instability."
        elif "Project Beta" in entities and "Budget Cut" in entities:
            summary += " Major focus: Project Beta is stalled due to financial constraints."
        elif "Alice" in entities and "Bob" in entities:
            summary += " Key Personnel: Alice and Bob are collaborating."

        return summary

    def reduce_summaries(self, query, summaries):
        """
        Simulate the Map-Reduce step for Global Search.
        """
        # In reality, this feeds all community summaries into the LLM context.
        final_answer = "Global Answer based on Graph Analysis:\n"
        final_answer += f"Query: '{query}'\n"
        final_answer += "-" * 40 + "\n"

        # Simple synthesis logic
        has_alpha_issue = any("Alpha" in s and "instability" in s for s in summaries)
        has_beta_issue = any("Beta" in s and "financial" in s for s in summaries)

        if "overall status" in query.lower() or "summary" in query.lower():
            if has_alpha_issue:
                final_answer += "- Critical Risk identified in Project Alpha (Technical).\n"
            if has_beta_issue:
                final_answer += "- Critical Risk identified in Project Beta (Financial).\n"
            final_answer += "- Cross-project resource contention is implied between Alice and Bob's teams."

        return final_answer

class GraphRAGSimulator:
    def __init__(self):
        self.llm = MockLLM()
        self.graph = SimpleGraph()
        self.communities = []
        self.community_summaries = {}

    def ingest(self, documents):
        print(f"--- Indexing {len(documents)} Documents ---")

        # 1. Entity Extraction & Graph Building
        print("1. Extracting Entities & Building Graph...")
        for doc in documents:
            _, rels = self.llm.extract_entities(doc)
            for u, v in rels:
                self.graph.add_edge(u, v)
                print(f"   Edge detected: {u} <--> {v}")

        # 2. Community Detection (Clustering)
        print("\n2. Detecting Communities (Leiden-ish)...")
        self.communities = self.graph.get_connected_components()
        for i, comm in enumerate(self.communities):
            print(f"   Community {i}: {comm}")

        # 3. Community Summarization
        print("\n3. Generating Community Summaries...")
        for i, comm in enumerate(self.communities):
            summary = self.llm.summarize_community(comm)
            self.community_summaries[i] = summary
            print(f"   Summary {i}: {summary}")

    def global_query(self, query):
        print(f"\n--- Executing Global Query: '{query}' ---")

        # 1. Gather all community summaries (Map step)
        all_summaries = list(self.community_summaries.values())

        # 2. Synthesize answer (Reduce step)
        answer = self.llm.reduce_summaries(query, all_summaries)

        print("Result:")
        print(answer)

# --- Simulation Execution ---

if __name__ == "__main__":
    # Mock Data: Disconnected reports that Vector RAG might struggle to connect globally
    docs = [
        "Alice is working late on Project Alpha to fix the Server Crash.",
        "Bob mentioned that the Budget Cut is affecting his ability to hire.",
        "Project Beta cannot proceed because of the recent Budget Cut.",
        "Charlie is helping Alice with the logs.",
        # Note: Alice connected to Alpha. Alpha connected to Crash.
        # Beta connected to Budget. Bob connected to Budget.
        # Implicitly, we have two main clusters (Technical vs Financial)
    ]

    rag = GraphRAGSimulator()
    rag.ingest(docs)
    rag.global_query("What is the overall status of the engineering department?")
