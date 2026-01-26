"""
Browser Use Simulation
----------------------
This script simulates the core logic of the 'browser-use' library:
1. An Agent that loops through Observe -> Reason -> Act.
2. A Mock Browser that returns a text-based representation of a webpage (like an Accessibility Tree).
3. A Mock LLM that "sees" the text state and decides the next action.

This runs with ZERO external dependencies (standard library only).
"""

import json
import time
from typing import Dict, List, Any, Optional

# --- 1. The Mock Browser (Playwright Replacement) ---

class MockBrowser:
    """
    Simulates a Headless Browser.
    Instead of rendering HTML, it holds a dictionary of 'Pages', where each page
    has a list of interactive elements (the 'Accessibility Tree').
    """
    def __init__(self):
        self.current_url = "about:blank"
        # The 'internet' is a dictionary of URL -> Element List
        self.pages = {
            "https://google.com": {
                "title": "Google",
                "elements": [
                    {"id": 1, "type": "Input", "name": "Search Query", "value": ""},
                    {"id": 2, "type": "Button", "name": "Google Search"},
                ]
            },
            "https://google.com/search?q=flights": {
                "title": "Google Search Results",
                "elements": [
                    {"id": 3, "type": "Link", "name": "Google Flights", "href": "https://flights.google.com"},
                    {"id": 4, "type": "Link", "name": "Kayak", "href": "https://kayak.com"},
                ]
            },
            "https://flights.google.com": {
                "title": "Google Flights",
                "elements": [
                    {"id": 5, "type": "Input", "name": "From", "value": "New York"},
                    {"id": 6, "type": "Input", "name": "To", "value": ""},
                    {"id": 7, "type": "Button", "name": "Search Flights"},
                ]
            },
            "https://flights.google.com/results": {
                "title": "Flight Results",
                "elements": [
                    {"id": 8, "type": "Text", "content": "Flight 1: $300 (United)"},
                    {"id": 9, "type": "Button", "name": "Book Flight 1"},
                    {"id": 10, "type": "Text", "content": "Flight 2: $450 (Delta)"},
                ]
            }
        }
        self.history = []

    def goto(self, url: str):
        print(f"  [Browser] Navigating to {url}...")
        if url in self.pages:
            self.current_url = url
            return True
        print(f"  [Browser] Error: 404 Not Found ({url})")
        return False

    def get_state(self) -> str:
        """
        Returns a text representation of the current page's interactive elements.
        This simulates the 'Vision/Accessibility Tree' extraction.
        """
        if self.current_url not in self.pages:
            return "Error: Page not found."

        page_data = self.pages[self.current_url]
        state_lines = [f"Title: {page_data['title']}", "Interactive Elements:"]

        for el in page_data['elements']:
            if el['type'] == 'Input':
                state_lines.append(f"[{el['id']}] Input '{el['name']}': value='{el.get('value', '')}'")
            elif el['type'] == 'Button':
                state_lines.append(f"[{el['id']}] Button '{el['name']}'")
            elif el['type'] == 'Link':
                state_lines.append(f"[{el['id']}] Link '{el['name']}' (href={el.get('href')})")
            elif el['type'] == 'Text':
                state_lines.append(f"     Text: {el['content']}")

        return "\n".join(state_lines)

    def execute_action(self, action: Dict[str, Any]):
        """
        Executes a Playwright-style action on the current page.
        """
        page_data = self.pages.get(self.current_url)
        if not page_data:
            return "Failed: No page loaded"

        act_type = action.get("action")
        target_id = action.get("id")

        # Find the element
        target_el = next((el for el in page_data['elements'] if el.get('id') == target_id), None)

        if not target_el:
            return f"Failed: Element [{target_id}] not found on current page."

        if act_type == "click":
            print(f"  [Browser] Clicked element [{target_id}] ({target_el.get('name', 'Unknown')})")

            # Simulate navigation if it's a link
            if target_el['type'] == 'Link':
                self.goto(target_el['href'])
            # Simulate state change for specific buttons (Hardcoded logic for simulation)
            elif target_el['name'] == "Google Search":
                 # In a real browser, this would be dynamic. Here we mock the transition.
                 # We assume the input was 'flights' for this demo.
                 self.goto("https://google.com/search?q=flights")
            elif target_el['name'] == "Search Flights":
                self.goto("https://flights.google.com/results")
            elif target_el['name'].startswith("Book"):
                print("  [Browser] Booking flow initiated... (Success)")
                return "Goal Achieved: Flight Booked"

            return "Clicked"

        elif act_type == "type":
            text = action.get("text")
            print(f"  [Browser] Typed '{text}' into element [{target_id}]")
            target_el['value'] = text
            return f"Typed '{text}'"

        return "Unknown Action"

# --- 2. The Mock LLM (Reasoning Engine) ---

class MockLLM:
    """
    Simulates the Agentic LLM (e.g., GPT-4o).
    It receives the State (String) and Goal (String), and outputs a JSON action.
    """
    def predict_next_action(self, state: str, goal: str) -> Dict[str, Any]:
        print("\n  [LLM] Thinking...")
        # Simple heuristic logic to simulate "Intelligence"

        # 1. If on Google Homepage -> Type 'flights' and Search
        if "Title: Google" in state and "Search Query" in state:
            # Check if we already typed it
            if "value=''" in state: # Input is empty
                return {"action": "type", "id": 1, "text": "flights"}
            else: # Input has value, click search
                return {"action": "click", "id": 2}

        # 2. If on Search Results -> Click Google Flights link
        if "Title: Google Search Results" in state:
            return {"action": "click", "id": 3}

        # 3. If on Google Flights -> Fill destination and Search
        if "Title: Google Flights" in state:
            if "To': value=''" in state:
                return {"action": "type", "id": 6, "text": "London"}
            else:
                return {"action": "click", "id": 7}

        # 4. If on Results -> Book the first flight
        if "Title: Flight Results" in state:
            return {"action": "click", "id": 9}

        return {"action": "stop", "reason": "I am confused or done."}

# --- 3. The Agent (Controller) ---

class BrowserAgent:
    def __init__(self, task: str):
        self.task = task
        self.browser = MockBrowser()
        self.llm = MockLLM()

    def run(self):
        print(f"🤖 Agent Started. Task: '{self.task}'")
        self.browser.goto("https://google.com") # Start at Google

        step = 1
        max_steps = 10

        while step <= max_steps:
            print(f"\n--- Step {step} ---")

            # 1. Observe
            state = self.browser.get_state()
            print(f"[State Observed]:\n{state}")

            # 2. Reason
            action = self.llm.predict_next_action(state, self.task)
            print(f"[LLM Decision]: {json.dumps(action)}")

            if action.get("action") == "stop":
                print("🛑 Agent decided to stop.")
                break

            # 3. Act
            result = self.browser.execute_action(action)
            print(f"[Execution Result]: {result}")

            if "Goal Achieved" in result:
                print("\n🎉 TASK COMPLETED SUCCESSFULLY!")
                return

            step += 1
            time.sleep(0.5) # Simulate latency

# --- Main Execution ---

if __name__ == "__main__":
    agent = BrowserAgent(task="Find a flight to London")
    agent.run()
