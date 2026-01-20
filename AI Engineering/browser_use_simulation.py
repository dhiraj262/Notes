"""
Browser Use Simulation
----------------------
This script simulates the core architecture of the "Browser Use" library.
It demonstrates how an Agent orchestrates an LLM and a Browser to perform tasks.
The real library uses Playwright for actual browser control and Vision-LLMs for decision making.
Here, we mock the Browser and LLM to show the control flow and state management.

Core Components:
1. Browser: Manages the state (URL, DOM, "Screenshot") and executes actions.
2. LLM: Receives the browser state and decides the next action based on the user's task.
3. Agent: The loop that connects the User Task, Browser, and LLM.
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# --- 1. The Mock Browser Component ---

@dataclass
class BrowserState:
    url: str
    dom_elements: List[str]  # Simplified DOM representation
    screenshot_placeholder: str = "<IMAGE_DATA>"

class MockBrowser:
    """
    Simulates a web browser (like Playwright).
    It maintains the current page state and executes actions.
    """
    def __init__(self):
        self.url = "about:blank"
        # We simulate a few "pages" with a simple dictionary state
        self.pages = {
            "about:blank": ["<input id='1'>Address Bar</input>", "<button id='2'>Go</button>"],
            "google.com": [
                "<img id='1' alt='Google Logo'>",
                "<input id='2' name='q'>Search Box</input>",
                "<button id='3'>Google Search</button>"
            ],
            "google.com/search?q=browser+use": [
                "<link id='1'>Browser Use - GitHub</link>",
                "<link id='2'>Browser Use - PyPI</link>",
                "<text id='3'>The easiest way to control browsers with AI...</text>"
            ],
            "github.com/browser-use": [
                "<text id='1'>browser-use/browser-use</text>",
                "<button id='2'>Star (75k)</button>",
                "<text id='3'>README.md</text>"
            ]
        }
        self.current_dom = self.pages["about:blank"]

    def get_state(self) -> BrowserState:
        return BrowserState(
            url=self.url,
            dom_elements=self.current_dom
        )

    def execute_action(self, action: Dict[str, Any]) -> str:
        """
        Executes a single action (e.g., {'click': '2'} or {'type': 'Browser Use', 'element': '2'}).
        Returns a result message.
        """
        action_type = list(action.keys())[0]
        params = action[action_type]

        print(f"  [Browser] Executing: {action}")

        if action_type == 'goto':
            self.url = params
            if self.url in self.pages:
                self.current_dom = self.pages[self.url]
                return f"Navigated to {self.url}"
            else:
                self.current_dom = ["<text>404 Not Found</text>"]
                return f"Navigated to {self.url} (404)"

        elif action_type == 'type':
            # Simulation: We just acknowledge the typing; in a real browser this updates the input field
            text = params.get('text')
            element_id = params.get('element')
            return f"Typed '{text}' into element #{element_id}"

        elif action_type == 'click':
            element_id = params
            # Hardcoded logic to simulate navigation flows based on clicks
            if self.url == "google.com" and element_id == '3':
                self.url = "google.com/search?q=browser+use"
                self.current_dom = self.pages[self.url]
                return "Clicked Search. Page loaded."

            if self.url == "google.com/search?q=browser+use" and element_id == '1':
                self.url = "github.com/browser-use"
                self.current_dom = self.pages[self.url]
                return "Clicked Result. Navigated to GitHub."

            return f"Clicked element #{element_id}"

        return "Unknown Action"

# --- 2. The Mock LLM Component ---

class MockLLM:
    """
    Simulates a Vision-LLM (like GPT-4o or Claude 3.5 Sonnet).
    It 'looks' at the state and the task, then outputs structured JSON actions.
    """
    def __init__(self):
        # We pre-script the intelligence for this specific simulation sequence
        self.step_counter = 0

    def predict(self, task: str, state: BrowserState) -> Dict[str, Any]:
        """
        Decides the next action based on the current step and state.
        In reality, this is a probabilistic generation.
        """
        self.step_counter += 1
        print(f"  [LLM] Analyzing state of {state.url}...")

        # Step 1: User wants to go to google
        if self.step_counter == 1:
            return {"goto": "google.com"}

        # Step 2: User wants to search. LLM sees the Search Box (id=2) and Button (id=3)
        if self.step_counter == 2:
            # First it types
            return {"type": {"text": "browser use", "element": "2"}}

        if self.step_counter == 3:
            # Then it clicks search
            return {"click": "3"}

        # Step 3: Search results are visible. LLM sees the GitHub link (id=1)
        if self.step_counter == 4:
            return {"click": "1"}

        # Step 4: We are on the GitHub page. Task complete?
        if "github.com" in state.url:
            return {"done": "I have navigated to the Browser Use GitHub page."}

        return {"done": "Stuck."}

# --- 3. The Agent Component ---

class Agent:
    """
    The orchestrator. It manages the loop: State -> LLM -> Action -> New State.
    """
    def __init__(self, task: str, browser: MockBrowser, llm: MockLLM):
        self.task = task
        self.browser = browser
        self.llm = llm
        self.history = []

    def run(self):
        print(f"🤖 Agent Started with task: '{self.task}'")
        print("-" * 50)

        for i in range(10):  # Safety limit
            # 1. Observation
            state = self.browser.get_state()
            print(f"\n📍 Step {i+1}: Current URL: {state.url}")
            print(f"   Visible Elements: {state.dom_elements}")

            # 2. Thought/Decision
            action = self.llm.predict(self.task, state)
            self.history.append(action)

            # 3. Check for completion
            if "done" in action:
                print(f"\n✅ Task Completed: {action['done']}")
                break

            # 4. Action Execution
            result = self.browser.execute_action(action)
            print(f"   Result: {result}")

            time.sleep(0.5) # Simulate network/processing delay

if __name__ == "__main__":
    # Initialize components
    browser = MockBrowser()
    llm = MockLLM()

    # Define the high-level task
    task = "Go to Google, search for 'browser use', and click the first result."

    # Run the agent
    agent = Agent(task=task, browser=browser, llm=llm)
    agent.run()
