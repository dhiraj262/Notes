import time
import json
import re

# --- 1. Mock Browser Environment (The "World") ---

class MockElement:
    def __init__(self, id, tag, text, interactive=False, value=""):
        self.id = id
        self.tag = tag
        self.text = text
        self.interactive = interactive
        self.value = value

    def __repr__(self):
        # Representation similar to what the LLM sees (Simplified DOM)
        state = ""
        if self.interactive:
            state = f"[{self.id}] "

        content = self.text
        if self.tag == "input":
            content = f"Input: {self.value or '(empty)'}"

        return f"{state}<{self.tag}>{content}</{self.tag}>"

class MockPage:
    def __init__(self):
        self.url = "https://google.com"
        self.elements = []
        self._load_google()

    def _load_google(self):
        self.url = "https://google.com"
        self.elements = [
            MockElement(1, "div", "Google Logo"),
            MockElement(2, "input", "", interactive=True), # Search bar
            MockElement(3, "button", "Google Search", interactive=True),
            MockElement(4, "button", "I'm Feeling Lucky", interactive=True),
        ]

    def _load_search_results(self, query):
        self.url = f"https://google.com/search?q={query}"
        self.elements = [
            MockElement(1, "div", f"Results for '{query}'"),
            MockElement(5, "a", "Python.org - Official Site", interactive=True),
            MockElement(6, "a", "Learn Python - Codecademy", interactive=True),
            MockElement(7, "a", "Python Tutorial - W3Schools", interactive=True),
        ]

    def _load_python_org(self):
        self.url = "https://python.org"
        self.elements = [
            MockElement(10, "h1", "Welcome to Python.org"),
            MockElement(11, "a", "Downloads", interactive=True),
            MockElement(12, "a", "Documentation", interactive=True),
            MockElement(13, "div", "Latest News: Python 3.14 Released"),
        ]

    def get_state(self):
        """Returns the simplified DOM for the Agent"""
        return "\n".join([str(e) for e in self.elements])

    def interact(self, action):
        """Executes the action on the page"""
        print(f"    [Browser] Executing: {action}")

        action_type = action.get("action")
        target_id = action.get("element_id")
        text = action.get("text", "")

        # Validate Element
        target = next((e for e in self.elements if e.id == target_id), None)
        if not target and action_type != "finish":
            return False, f"Element [{target_id}] not found."

        if action_type == "type":
            target.value = text
            return True, f"Typed '{text}' into [{target_id}]"

        elif action_type == "click":
            # Simulate navigation logic based on clicks
            if "Google Search" in target.text:
                # Find what was typed in the input
                input_el = next((e for e in self.elements if e.tag == "input"), None)
                query = input_el.value if input_el else "nothing"
                self._load_search_results(query)
                return True, f"Clicked Search. Navigated to Results for '{query}'"

            elif "Python.org" in target.text:
                self._load_python_org()
                return True, "Clicked Link. Navigated to Python.org"

            return True, f"Clicked [{target_id}] ({target.text})"

        elif action_type == "finish":
            return True, "Task Completed."

        return False, "Unknown action"

# --- 2. Mock Agent (The "Brain") ---

class MockLLM:
    """Simulates the LLM's reasoning process"""

    def predict_action(self, state, goal):
        # Heuristic / Rule-based logic to simulate LLM reasoning

        # 1. If on Google Homepage -> Type query
        if "Google Logo" in state and "Input: (empty)" in state:
            return {
                "thought": "I am on Google. I need to type the search query.",
                "action": "type",
                "element_id": 2, # The input
                "text": "Python programming"
            }

        # 2. If typed query -> Click Search
        if "Input: Python programming" in state:
            return {
                "thought": "I have typed the query. Now I need to click Search.",
                "action": "click",
                "element_id": 3 # The search button
            }

        # 3. If on Results page -> Click the Python.org link
        if "Results for" in state:
            return {
                "thought": "I see the search results. I will click on the official Python site.",
                "action": "click",
                "element_id": 5 # Python.org link
            }

        # 4. If on Python.org -> Finish
        if "Welcome to Python.org" in state:
             return {
                "thought": "I have arrived at Python.org. Goal achieved.",
                "action": "finish",
                "element_id": None
            }

        return {"thought": "I am lost.", "action": "finish", "element_id": None}

# --- 3. The Browser Use Loop (Controller) ---

def run_agent_simulation():
    print("--- Starting Browser Use Simulation ---\n")

    # Initialize
    browser = MockPage()
    llm = MockLLM()
    goal = "Go to Python.org"

    print(f"🎯 User Goal: {goal}")

    step = 1
    max_steps = 10

    while step <= max_steps:
        print(f"\n--- Step {step} ---")

        # 1. Observe State
        current_state = browser.get_state()
        print(f"👀 Agent sees:\n{current_state}")

        # 2. Reason (LLM Call)
        response = llm.predict_action(current_state, goal)
        print(f"🧠 Agent Thought: {response['thought']}")

        # 3. Act
        if response['action'] == 'finish':
            print("✅ Agent decided to finish.")
            break

        success, msg = browser.interact(response)
        print(f"👉 Action Result: {msg}")

        if not success:
            print("❌ Action failed, stopping.")
            break

        step += 1
        time.sleep(1) # Simulate network/processing delay

if __name__ == "__main__":
    run_agent_simulation()
