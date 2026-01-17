"""
Browser Use Simulation
----------------------
This script simulates the core architecture of the 'Browser Use' library.
It demonstrates the "Observe-Think-Act" loop where an Agent controls a Browser
via an LLM's structured output.

Concept:
1. Browser: Provides state (Screenshot/DOM).
2. LLM: Analyzes state, decides next action.
3. Controller: Executes the action.

Note: This is a simulation using mocks. No actual browser (Playwright) or LLM (OpenAI) is used.
"""

import json
import time
from typing import List, Dict, Any, Optional

# --- 1. Mock Browser Environment ---
class MockBrowser:
    """
    Simulates a web browser (Playwright wrapper).
    Keeps track of the 'current page' and its interactive elements.
    """
    def __init__(self):
        self.current_url = "https://example-flight-booker.com"
        self.page_state = "home" # home, search_results, checkout

    def get_state(self) -> Dict[str, Any]:
        """Returns a simulated 'Screenshot' (description) and DOM tree."""
        if self.page_state == "home":
            return {
                "url": self.current_url,
                "screenshot_desc": "Homepage with a search form.",
                "dom": [
                    {"id": 1, "type": "input", "name": "origin", "value": ""},
                    {"id": 2, "type": "input", "name": "destination", "value": ""},
                    {"id": 3, "type": "button", "name": "Search Flights"}
                ]
            }
        elif self.page_state == "search_results":
            return {
                "url": self.current_url + "/search",
                "screenshot_desc": "List of flights. Top result is $300.",
                "dom": [
                    {"id": 4, "type": "button", "name": "Select Flight ($300)"},
                    {"id": 5, "type": "button", "name": "Select Flight ($500)"}
                ]
            }
        elif self.page_state == "checkout":
            return {
                "url": self.current_url + "/checkout",
                "screenshot_desc": "Checkout page. Success message.",
                "dom": [
                    {"id": 6, "type": "text", "content": "Booking Confirmed!"}
                ]
            }
        return {}

    def execute(self, action_name: str, params: Dict[str, Any]):
        """Simulates executing an action on the browser."""
        print(f"  [Browser] Executing: {action_name} with {params}")

        # State transitions for the simulation
        if self.page_state == "home":
            if action_name == "click_element" and params.get("index") == 3:
                print("  [Browser] ...Transitioning to Search Results...")
                self.page_state = "search_results"

        elif self.page_state == "search_results":
            if action_name == "click_element" and params.get("index") == 4:
                print("  [Browser] ...Transitioning to Checkout...")
                self.page_state = "checkout"

# --- 2. Mock LLM (The Brain) ---
class MockLLM:
    """
    Simulates a Multimodal LLM (e.g., GPT-4o).
    In a real app, this would send the DOM + Screenshot to an API.
    Here, we use simple logic to return the 'correct' action for the demo.
    """
    def predict_action(self, state: Dict[str, Any], goal: str) -> Dict[str, Any]:
        dom = state.get("dom", [])
        page_desc = state.get("screenshot_desc", "")

        print(f"  [LLM] Seeing: {page_desc}")

        # Heuristic logic to simulate "intelligence"
        if "Homepage" in page_desc:
            # If on home, we need to fill inputs?
            # For simplicity, let's assume inputs are pre-filled or we just click search.
            # In a full simulation, we'd have 'type_text' actions first.
            # Let's just click the search button (id: 3).
            return {"action": "click_element", "params": {"index": 3}, "thought": "I see the search button. Clicking it to find flights."}

        elif "List of flights" in page_desc:
            # Click the first/cheapest flight (id: 4)
            return {"action": "click_element", "params": {"index": 4}, "thought": "Found a flight for $300. Selecting it."}

        elif "Checkout" in page_desc:
            return {"action": "done", "params": {}, "thought": "Booking confirmed. Task complete."}

        return {"action": "done", "params": {}, "thought": "I am confused."}

# --- 3. The Agent (The Core Loop) ---
class Agent:
    def __init__(self, task: str):
        self.task = task
        self.browser = MockBrowser()
        self.llm = MockLLM()
        self.history = []

    def run(self):
        print(f"--- Starting Agent Task: {self.task} ---")
        step = 0
        max_steps = 5

        while step < max_steps:
            step += 1
            print(f"\nStep {step}:")

            # 1. Observe
            state = self.browser.get_state()

            # 2. Think
            response = self.llm.predict_action(state, self.task)
            action_name = response["action"]
            params = response["params"]
            thought = response["thought"]

            print(f"  [Agent Thought] {thought}")

            # 3. Act
            if action_name == "done":
                print("--- Task Completed Successfully ---")
                return

            self.browser.execute(action_name, params)
            time.sleep(0.5) # Simulate latency

        print("--- Max Steps Reached ---")

# --- Run Simulation ---
if __name__ == "__main__":
    agent = Agent(task="Find the cheapest flight to NYC")
    agent.run()
