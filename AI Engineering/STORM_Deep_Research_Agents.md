# STORM & Deep Research Agents: The End of "Blue Links"

## 1. Latest Context
As of early 2025, the AI industry is witnessing a massive pivot from **"Chatbots"** (System 1) to **"Deep Research Agents"** (System 2). OpenAI's release of "Deep Research" (formerly Operator) and the rise of Perplexity Pro have normalized the expectation that an AI should not just *retrieve* information, but *synthesize* comprehensive reports that would take a human hours to write.

*   **Trending on GitHub**: Repositories like `stanford-oval/storm` and `open-deep-research` are trending, offering open-source alternatives to proprietary research agents.
*   **The Shift**: We are moving from **RAG (Retrieval-Augmented Generation)**, which fetches a few snippets for a quick answer, to **Agentic Research**, which performs iterative, multi-step information gathering, cross-referencing, and outlining.

## 2. What, Why, How

### What is STORM?
**STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking)** is a framework proposed by Stanford researchers to generate Wikipedia-quality long-form articles. It fundamentally changes how LLMs approach writing by mimicking the human *pre-writing* process.

### Why do we need it?
*   **The "Surface-Level" Problem**: Standard RAG pipelines are lazy. If you ask "Explain the impact of AI on jobs," they grab the top 3 Google results and summarize them. They miss nuance, dissenting opinions, and deep structural details.
*   **Perspective Blindness**: A single query often reflects a single bias. To write a balanced report, one must ask questions from the perspective of an *Economist*, an *Ethicist*, and a *Labor Union Leader*.
*   **Hallucination in Long-Form**: LLMs struggle to maintain coherence over 2,000+ words without a rigid outline.

### How does it work?
STORM breaks the process into two distinct phases:
1.  **Pre-Writing (Research & Outlining)**:
    *   **Perspective Discovery**: The system analyzes the topic to find diverse viewpoints (e.g., for "Space Mining", it identifies "Environmentalist", "Venture Capitalist", "Space Lawyer").
    *   **Simulated Conversation**: It instantiates "Perspective Agents" that interview a "Topic Expert" (powered by a Search Engine) to ask targeted questions.
    *   **Outline Generation**: The collected information is organized into a hierarchical outline.
2.  **Writing**: The system generates the article section-by-section based on the outline and cited references.

## 3. Use Cases
*   **Market Intelligence**: "Generate a 50-page report on the competitive landscape of Solid State Batteries."
*   **Academic Review**: "Synthesize all papers from 2024 related to Transformer efficiency improvements."
*   **Content Marketing**: Creating detailed, SEO-optimized whitepapers that actually contain novel insights rather than generic fluff.
*   **Due Diligence**: Venture Capitalists using agents to scour the web for red flags on a target startup.

## 4. Real World Examples

### Example 1: The "Wikipedia" Writer
In the STORM paper, the system was tasked with writing an article on "The 2022 Winter Olympics".
*   *Standard RAG*: Wrote a generic summary of the opening ceremony and medal counts.
*   *STORM*: Discovered a "Geopolitical Perspective" and asked about the diplomatic boycotts. It discovered an "Environmental Perspective" and asked about the artificial snow usage. The result was a comprehensive, multi-faceted article comparable to human-edited Wikipedia pages.

### Example 2: Perplexity Deep Research
Perplexity's "Deep Search" feature essentially implements this pattern. When a user asks a vague question, the system doesn't just answer; it asks *clarifying questions* back to the user or autonomously generates sub-queries to different domains (Reddit, News, Academic Papers) to build a full picture.

## 5. Future Readiness & Critique
*   **Readiness**: **High**. The components (LLMs, Search APIs like Tavily/Serper, Orchestration frameworks like LangGraph) are all mature.
*   **Critique**:
    *   **Time & Cost**: Deep Research is expensive. A single report might trigger 50+ search queries and 100k+ tokens. It's not for "What's the weather?"
    *   **Search Bias**: The "Expert" is still limited by what's indexed on Google/Bing. If the info isn't public, the agent can't find it.
    *   **Echo Chambers**: If the "Perspectives" are derived from the LLM's training data, it might miss truly novel or fringe viewpoints that exist in reality but aren't in the model's weights.

## 6. Evolution & Problem Solved
*   **Problem Solved**: **"The Shallow Summary."** LLMs are great summarizers but poor researchers. They tend to average out information, losing the "spikes" of specific insights. STORM forces depth by explicitly querying for it.
*   **Evolution**:
    1.  **Search Engines**: 10 blue links (User does the synthesis).
    2.  **Generative Search (Perplexity)**: Summarize top 5 links (System 1 synthesis).
    3.  **Agentic RAG**: Loop until answer is found (Primitive System 2).
    4.  **Deep Research (STORM)**: **Structured, Perspective-Driven Investigation (Advanced System 2)**.

## 7. Deep Dive: Perspective-Driven Question Asking

### 7.1 The Mechanism
The core innovation of STORM is replacing a generic "Researcher" with specific personas.

1.  **Topic**: "Remote Work"
2.  **Perspective Generation**:
    *   Persona A: **Corporate Manager** (Interests: Productivity, Culture)
    *   Persona B: **Digital Nomad** (Interests: Visa laws, Internet speed)
    *   Persona C: **Urban Planner** (Interests: Traffic patterns, Real estate)
3.  **Conversation Loop**:
    *   *Manager Agent*: "How does remote work impact junior employee mentorship?"
    *   *Search Expert*: [Queries: "remote work mentorship challenges data"] -> Returns snippets.
    *   *Manager Agent*: "What are the proven solutions to this?" (Follow-up)
    *   *Search Expert*: [Queries: "remote mentorship best practices"] -> Returns snippets.
4.  **Synthesis**: The answers are stored not as a blob of text, but tagged by the perspective that asked them, ensuring the final outline covers all angles.

### 7.2 Architecture Diagram

```mermaid
flowchart TD
    subgraph PreWriting ["Phase 1: Pre-Writing"]
        Topic[User Topic] --> GenPers[Generate Perspectives]
        GenPers --> P1[Perspective: Economist]
        GenPers --> P2[Perspective: Ethicist]
        GenPers --> P3[Perspective: Historian]

        subgraph Conv ["Conversation Simulation"]
            P1 <-->|Ask/Answer| Expert[Topic Expert (Search Engine)]
            P2 <-->|Ask/Answer| Expert
            P3 <-->|Ask/Answer| Expert
        end

        Expert -->|Collected Info| KB[Knowledge Bank]
        KB --> OutlineGen[Outline Generator]
    end

    subgraph Writing ["Phase 2: Writing"]
        OutlineGen -->|Section 1| Writer[Section Writer]
        OutlineGen -->|Section 2| Writer
        OutlineGen -->|Section 3| Writer
        Writer -->|Refine| Article[Final Article]
    end
```

### 7.3 Simulation Code
This code simulates the "Perspective Discovery" and "Conversation" phases of STORM.

```python
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
```

## 9. Pros, Cons & Industry Usage

### Pros
*   **Completeness**: It's much harder to miss a critical angle when you explicitly search for it.
*   **Structure**: The generated articles have a logical flow, unlike the "stream of consciousness" output of raw LLMs.
*   **Trust**: Citations are gathered *during* the research phase, making them more reliable than post-hoc citations.

### Cons
*   **Complexity**: Requires orchestrating multiple LLM calls, state management, and robust error handling.
*   **Speed**: Generating a STORM article can take 1-5 minutes, whereas a ChatGPT answer is instant.

### Industry Usage
*   **Stanford OVAL**: The original creators of STORM.
*   **Perplexity**: Uses similar techniques for their Pro Search.
*   **You.com**: "Research Mode" implements multi-step reasoning.
*   **Enterprise Knowledge Bases**: Companies using this to generate internal wikis from slack history and documents.

## 9. References
*   **STORM Paper**: [Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models](https://arxiv.org/abs/2402.14207)
*   **GitHub Repository**: [stanford-oval/storm](https://github.com/stanford-oval/storm)
*   **Perplexity Deep Research**: [Perplexity Blog](https://www.perplexity.ai/hub/blog/perplexity-pro)
*   **OpenAI Deep Research**: [OpenAI Blog](https://openai.com/blog)
