import time
import random

class StormSimulation:
    def __init__(self, topic):
        self.topic = topic
        self.knowledge_bank = []

    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def generate_perspectives(self):
        """
        Simulates an LLM identifying diverse perspectives for a topic.
        """
        self.log(f"🧠 Analyzing topic: '{self.topic}' to find diverse perspectives...")
        time.sleep(1)
        # Mock LLM Output
        perspectives = [
            "Economic Analyst",
            "Environmental Scientist",
            "Public Policy Expert"
        ]
        self.log(f"✅ Identified Perspectives: {', '.join(perspectives)}")
        return perspectives

    def simulate_conversation(self, perspective):
        """
        Simulates the multi-turn conversation between a Perspective Agent and a Search Expert.
        """
        self.log(f"\n🎤 Starting interview with Perspective: {perspective}")

        # 1. Perspective Agent asks a question based on their bias
        question = self._generate_question(perspective)
        self.log(f"   👤 {perspective}: \"{question}\"")

        # 2. Search Expert finds information
        info = self._search_expert_response(question)
        self.log(f"   🤖 Search Expert: Found {len(info)} sources. Summary: {info[:60]}...")

        # 3. Perspective Agent asks a follow-up
        follow_up = self._generate_follow_up(perspective, info)
        self.log(f"   👤 {perspective}: \"{follow_up}\"")

        # 4. Search Expert finds more information
        more_info = self._search_expert_response(follow_up)
        self.log(f"   🤖 Search Expert: Found specific data. Summary: {more_info[:60]}...")

        # Store in Knowledge Bank
        self.knowledge_bank.append({
            "perspective": perspective,
            "q1": question,
            "a1": info,
            "q2": follow_up,
            "a2": more_info
        })

    def _generate_question(self, perspective):
        # Mocking LLM question generation
        templates = {
            "Economic Analyst": f"What are the long-term cost implications of {self.topic}?",
            "Environmental Scientist": f"What is the ecological footprint of {self.topic}?",
            "Public Policy Expert": f"What regulatory frameworks currently govern {self.topic}?"
        }
        return templates.get(perspective, f"Tell me about {self.topic} from your view.")

    def _generate_follow_up(self, perspective, previous_info):
        # Mocking LLM follow-up
        templates = {
            "Economic Analyst": "Are there historical precedents for this market shift?",
            "Environmental Scientist": "How can these emissions be mitigated?",
            "Public Policy Expert": "Which countries have successfully regulated this?"
        }
        return templates.get(perspective, "Can you elaborate on that?")

    def _search_expert_response(self, query):
        time.sleep(0.5)
        # Mocking Search Engine retrieval
        return f"[Fact Sheet retrieved for query: '{query}']... Data points included."

    def generate_outline(self):
        self.log("\n📝 Generating Outline based on Knowledge Bank...")
        time.sleep(1)
        print("\n--- GENERATED OUTLINE ---")
        print(f"# Deep Dive: {self.topic}")
        for entry in self.knowledge_bank:
            print(f"## Section: The {entry['perspective']} View")
            print(f"  - Key Question: {entry['q1']}")
            print(f"  - Key Insight: {entry['a1']}")
            print(f"  - Deep Dive: {entry['a2']}")
        print("-------------------------")

# Run Simulation
if __name__ == "__main__":
    storm = StormSimulation("Asteroid Mining")
    perspectives = storm.generate_perspectives()

    for p in perspectives:
        storm.simulate_conversation(p)

    storm.generate_outline()
