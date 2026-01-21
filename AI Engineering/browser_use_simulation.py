import time
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# --- Configuration & Styling ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_name: str, details: str):
    print(f"{Colors.BOLD}{Colors.OKCYAN}[{step_name}]{Colors.ENDC} {details}")

def print_action(action: str):
    print(f"{Colors.OKGREEN}  -> ACTION: {action}{Colors.ENDC}")

def print_observation(obs: str):
    print(f"{Colors.OKBLUE}  -> OBSERVE: {obs}{Colors.ENDC}")

# --- Mock Infrastructure (Simulating Playwright + Browser) ---

@dataclass
class Element:
    id: str
    description: str
    actionable: bool = True

class MockPage:
    def __init__(self, url: str, title: str, elements: List[Element]):
        self.url = url
        self.title = title
        self.elements = elements

    def get_dom_snapshot(self) -> str:
        """Simulates extracting the Accessibility Tree / Simplified DOM"""
        snapshot = f"Page: {self.title} ({self.url})\n"
        snapshot += "Interactive Elements:\n"
        for el in self.elements:
            if el.actionable:
                snapshot += f" - [{el.id}] {el.description}\n"
        return snapshot

class MockBrowser:
    def __init__(self):
        self.current_page: Optional[MockPage] = None
        self.history: List[str] = []
        # Define the "Internet" (Map of interactions)
        self._internet_map = {
            "start": MockPage("https://google.com", "Google Search", [
                Element("input_search", "Search Bar Input"),
                Element("btn_search", "Google Search Button")
            ]),
            "search_results": MockPage("https://google.com/search?q=coffee", "Search Results", [
                Element("link_1", "Link: Best Coffee in Town"),
                Element("link_2", "Link: Wikipedia - Coffee")
            ]),
            "coffee_shop": MockPage("https://bestcoffee.com", "Best Coffee Shop", [
                Element("btn_order", "Button: Order Latte ($5)"),
                Element("btn_menu", "Button: View Menu")
            ]),
            "order_success": MockPage("https://bestcoffee.com/success", "Order Confirmed", [
                Element("txt_msg", "Text: Your order has been placed!", actionable=False),
                Element("btn_home", "Button: Return Home")
            ])
        }
        self.goto("start")

    def goto(self, key: str):
        if key in self._internet_map:
            self.current_page = self._internet_map[key]
            self.history.append(self.current_page.url)
            return True
        return False

    def execute_action(self, action: Dict[str, Any]) -> str:
        """Simulates Playwright actions"""
        act_type = action.get("type")
        target = action.get("target")

        if not self.current_page:
            return "Error: No page open."

        # Logic to transition state based on actions
        # This mocks the "Server Side" logic of the websites
        if self.current_page.url == "https://google.com":
            if act_type == "type" and target == "input_search":
                return f"Typed '{action.get('value')}' into search bar."
            if act_type == "click" and target == "btn_search":
                self.goto("search_results")
                return "Clicked Search. Loading results..."

        elif self.current_page.url == "https://google.com/search?q=coffee":
            if act_type == "click" and target == "link_1":
                self.goto("coffee_shop")
                return "Clicked 'Best Coffee'. Navigating..."

        elif self.current_page.url == "https://bestcoffee.com":
            if act_type == "click" and target == "btn_order":
                self.goto("order_success")
                return "Clicked 'Order Latte'. Processing payment..."

        return "Action completed (No navigation)."

    def get_state(self) -> str:
        return self.current_page.get_dom_snapshot() if self.current_page else "No Page"

# --- Mock LLM (The "Brain") ---

class MockLLM:
    """
    Simulates a Vision-Language Model (VLM) like GPT-4o.
    In a real app, this would send the DOM/Screenshot to the API.
    Here, we use a simple heuristic to pick the right action for the demo.
    """
    def predict_action(self, goal: str, dom_state: str) -> Dict[str, Any]:
        # Heuristic Logic to simulate "Reasoning"
        if "Google Search" in dom_state:
            # Step 1: Need to search
            if "Typed" not in goal: # A bit of state tracking hack for demo
                return {"type": "type", "target": "input_search", "value": "Best Coffee"}
            return {"type": "click", "target": "btn_search"}

        if "input_search" in dom_state and "Google Search" in dom_state:
             # Wait, the logic above is a bit simplified. Let's make it state-independent mostly.
             pass

        # Let's use specific triggers based on the content to simulate "understanding"
        if "input_search" in dom_state:
             return {"type": "type", "target": "input_search", "value": "Best Coffee"}

        if "btn_search" in dom_state: # This might conflict with input, but let's assume the agent types then clicks.
             # In a real loop, the agent remembers history.
             # We will handle the "Type then Click" sequence in the main loop or make the mock smarter.
             pass

        # Refined Mock Logic
        if "Google Search" in dom_state:
             # If we haven't typed yet (we can't easily know internal state here without passing history),
             # let's just assume the Agent is smart.
             # Actually, let's use a generator or iterator to simulate the "Thought Process" sequence for this specific scenario.
             pass

        return {} # Placeholder

class ScriptedLLM(MockLLM):
    """
    A deterministic LLM for the simulation to ensure the demo flows correctly.
    """
    def __init__(self):
        self.step = 0

    def predict_action(self, goal: str, dom_state: str) -> Dict[str, Any]:
        """
        Returns the next action based on the 'step' of the script.
        """
        thought = ""
        action = {}

        if "Google Search" in dom_state:
            if self.step == 0:
                thought = "I see a search bar. I need to type 'Best Coffee' to find a shop."
                action = {"type": "type", "target": "input_search", "value": "Best Coffee"}
                self.step += 1
            elif self.step == 1:
                thought = "I have typed the query. Now I need to click the Search button."
                action = {"type": "click", "target": "btn_search"}
                self.step += 1

        elif "Search Results" in dom_state:
            thought = "I see search results. 'Best Coffee in Town' looks promising."
            action = {"type": "click", "target": "link_1"}

        elif "Best Coffee Shop" in dom_state:
            thought = "I am on the coffee shop page. I see an 'Order Latte' button. That aligns with the goal."
            action = {"type": "click", "target": "btn_order"}

        elif "Order Confirmed" in dom_state:
            thought = "The order is confirmed. My task is done."
            action = {"type": "finish"}

        print(f"{Colors.WARNING}  [Brain] Thought: {thought}{Colors.ENDC}")
        return action

# --- Agent (The Orchestrator) ---

class Agent:
    def __init__(self, goal: str, browser: MockBrowser, llm: MockLLM):
        self.goal = goal
        self.browser = browser
        self.llm = llm

    def run(self):
        print(f"{Colors.HEADER}--- Starting Agent Simulation ---{Colors.ENDC}")
        print(f"Goal: {self.goal}")

        max_steps = 10
        for i in range(max_steps):
            print("\n------------------------------------------------")
            print_step(f"Step {i+1}", "Analyzing State...")

            # 1. Get State (Vision/DOM)
            state = self.browser.get_state()
            print_observation(state.replace('\n', ' | '))

            # 2. Get Decision (LLM)
            action = self.llm.predict_action(self.goal, state)

            if action.get("type") == "finish":
                print(f"{Colors.OKGREEN}Goal Achieved!{Colors.ENDC}")
                break

            if not action:
                print(f"{Colors.FAIL}Agent got confused. Stopping.{Colors.ENDC}")
                break

            # 3. Execute Action (Browser)
            print_action(str(action))
            result = self.browser.execute_action(action)
            print(f"  -> Result: {result}")

            time.sleep(1) # Simulate network/processing delay

if __name__ == "__main__":
    # Setup
    browser = MockBrowser()
    llm = ScriptedLLM() # Using the scripted brain for the demo

    # Run
    agent = Agent(
        goal = "Go to Google, find a coffee shop, and order a Latte.",
        browser = browser,
        llm = llm
    )

    agent.run()
