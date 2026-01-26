import json
import random
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Optional

# --- 1. MOCK BROWSER INFRASTRUCTURE ---

@dataclass
class DOMElement:
    index: int
    tag: str
    text: str
    attributes: Dict[str, str]

    def __repr__(self):
        # Emulate the "Accessibility Tree" string representation
        return f"[{self.index}] {self.tag.upper()}: {self.text}"

class MockBrowser:
    """
    Simulates a Playwright browser instance.
    Instead of rendering HTML, it maintains a list of 'Actionable Elements'
    that changes based on interactions.
    """
    def __init__(self):
        self.url = "https://www.fake-travel-site.com"
        self.elements: List[DOMElement] = []
        self.state_name = "home" # home, search_results, checkout
        self._refresh_dom()

    def _refresh_dom(self):
        """Generates a fake DOM based on the current state."""
        self.elements = []

        if self.state_name == "home":
            self.elements = [
                DOMElement(1, "button", "One Way", {"selected": "false"}),
                DOMElement(2, "button", "Round Trip", {"selected": "true"}),
                DOMElement(3, "input", "From City", {"value": ""}),
                DOMElement(4, "input", "To City", {"value": ""}),
                DOMElement(5, "button", "Search Flights", {})
            ]
        elif self.state_name == "search_results":
            self.elements = [
                DOMElement(10, "text", "Flight AA101 - $300", {}),
                DOMElement(11, "button", "Select Flight AA101", {}),
                DOMElement(12, "text", "Flight UA202 - $450", {}),
                DOMElement(13, "button", "Select Flight UA202", {})
            ]
        elif self.state_name == "checkout":
            self.elements = [
                DOMElement(20, "text", "Total: $300", {}),
                DOMElement(21, "input", "Credit Card Number", {"value": ""}),
                DOMElement(22, "button", "Pay Now", {})
            ]

    def get_accessibility_tree(self) -> str:
        """Returns the text representation of the DOM seen by the LLM."""
        return "\n".join([str(e) for e in self.elements])

    def execute_action(self, action: Dict) -> str:
        """
        Simulates the effect of an action on the browser state.
        Supported actions: click, type
        """
        act_type = action.get("action")
        index = action.get("index")
        text = action.get("text", "")

        # Find element
        target = next((e for e in self.elements if e.index == index), None)
        if not target:
            return f"ERROR: Element [{index}] not found."

        print(f"  [Browser] Executing: {act_type.upper()} on '{target.text}'")

        if act_type == "click":
            if self.state_name == "home" and target.text == "Search Flights":
                self.state_name = "search_results"
                self._refresh_dom()
                return "Navigated to Search Results."
            elif self.state_name == "search_results" and "Select" in target.text:
                self.state_name = "checkout"
                self._refresh_dom()
                return "Navigated to Checkout."
            elif self.state_name == "checkout" and target.text == "Pay Now":
                return "Payment Processed. Task Complete."
            return f"Clicked {target.text} (No navigation)."

        elif act_type == "type":
            target.attributes["value"] = text
            return f"Typed '{text}' into {target.text}."

        return "Unknown Action."

# --- 2. MOCK LLM (AGENT BRAIN) ---

class MockLLM:
    """
    Simulates a Vision/Language Model (e.g., GPT-4o).
    In a real scenario, this sends the prompt to OpenAI/Anthropic.
    Here, we use a simple heuristic rule-based system to simulate 'reasoning'.
    """
    def __init__(self):
        pass

    def predict_action(self, task: str, dom_tree: str) -> Dict:
        """
        Decides the next action based on the task and current DOM.
        """
        print("\n  [LLM] Thinking...")

        # Heuristic Logic to simulate "Reasoning"
        if "To City" in dom_tree and "Search Flights" in dom_tree:
            # We are on home page

            # Check if "To City" is already filled
            # The DOM string will look like: "[4] INPUT: To City (Value: NYC)" if filled
            to_city_filled = "Value: NYC" in dom_tree

            if not to_city_filled:
                 # Find index of "To City"
                 match = re.search(r"\[(\d+)\] INPUT: To City", dom_tree)
                 if match:
                     return {"action": "type", "index": int(match.group(1)), "text": "NYC"}

            # If we already typed, click search.
            match = re.search(r"\[(\d+)\] BUTTON: Search Flights", dom_tree)
            if match:
                return {"action": "click", "index": int(match.group(1))}

        elif "Select Flight" in dom_tree:
            # We are on results page. Pick the cheap one ($300).
            match = re.search(r"\[(\d+)\] BUTTON: Select Flight AA101", dom_tree)
            if match:
                return {"action": "click", "index": int(match.group(1))}

        elif "Credit Card" in dom_tree:
            # Checkout
            match = re.search(r"\[(\d+)\] BUTTON: Pay Now", dom_tree)
            if match:
                return {"action": "click", "index": int(match.group(1))}

        # Fallback random action (should not happen in this controlled sim)
        return {"action": "wait"}

# --- 3. AGENT ORCHESTRATOR ---

class Agent:
    def __init__(self, task: str):
        self.task = task
        self.browser = MockBrowser()
        self.llm = MockLLM()
        self.history = []

    def step(self):
        """Runs one iteration of the Observe-Think-Act loop."""
        # 1. Observe
        dom_tree = self.browser.get_accessibility_tree()
        print(f"\n--- STATE: {self.browser.state_name.upper()} ---")
        print(dom_tree)

        # 2. Think
        # In a real agent, we'd pass previous history to avoid loops.
        # For this mock, the LLM state logic handles it partially, but we need to track state changes.

        # HACK: To simulate sequence on the "Home" page, we need to know if we already typed.
        # In real Browser Use, the browser state (value="NYC") is visible in the tree.
        # Let's update MockLLM to look for value="NYC" if I added it to the DOM string.
        # But my DOM string doesn't show attributes. Let's fix the MockLLM logic or the DOM repr.

        # Let's improve the DOM repr to show values for inputs
        # (This is dynamic monkey-patching for the simulation logic flow)
        pass

        action = self.llm.predict_action(self.task, dom_tree)

        # Simple State Management for the Simulation Loop to progress:
        # If the LLM suggests typing "NYC", but we are stuck in a loop because the DOM didn't update to show "NYC",
        # We need to manually force the next step in this mock or make the mock smarter.
        # Let's make the MockLLM smarter:
        # If "To City" has no value, Type. If it has value, Click Search.
        # Wait, the DOMElement repr doesn't show value. Let's update it.

        # 3. Act
        result = self.browser.execute_action(action)
        self.history.append((action, result))
        print(f"  [Result] {result}")

        return result

    def run(self, max_steps=5):
        print(f"Task: {self.task}")
        for i in range(max_steps):
            result = self.step()
            if "Task Complete" in result:
                print("\n✅ MISSION ACCOMPLISHED")
                return
            time.sleep(0.5)
        print("\n❌ Max steps reached")

# Fix DOM Representation to include values (Simulating Browser Use 'verbose' mode)
def improved_repr(self):
    base = f"[{self.index}] {self.tag.upper()}: {self.text}"
    if self.tag == "input" and self.attributes.get("value"):
        base += f" (Value: {self.attributes['value']})"
    return base

DOMElement.__repr__ = improved_repr


if __name__ == "__main__":
    # Simulate a user asking to book a flight
    agent = Agent("Book the cheapest flight to NYC")

    # We need to guide the MockLLM state a bit better since it's stateless.
    # The 'run' loop works, but the MockLLM needs to see the effect of previous actions.
    # Since MockBrowser updates the element attributes in 'type', the 'improved_repr' will show it.

    agent.run()
