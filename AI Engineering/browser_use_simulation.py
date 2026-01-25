import time
import json
import re

class MockBrowser:
    def __init__(self):
        self.current_url = "about:blank"
        # Simulated "Internet"
        self.pages = {
            "https://www.google.com": {
                "title": "Google",
                "elements": [
                    {"id": 1, "type": "input", "name": "q", "value": "", "placeholder": "Search Google"},
                    {"id": 2, "type": "button", "name": "btnK", "text": "Google Search"}
                ]
            },
            "https://www.google.com/search?q=DeepSeek": {
                "title": "DeepSeek - Google Search",
                "elements": [
                    {"id": 3, "type": "link", "text": "DeepSeek - Incentivizing Reasoning", "href": "https://deepseek.com"},
                    {"id": 4, "type": "link", "text": "DeepSeek GitHub", "href": "https://github.com/deepseek-ai"}
                ]
            },
            "https://deepseek.com": {
                "title": "DeepSeek Homepage",
                "elements": [
                    {"id": 5, "type": "text", "content": "Welcome to DeepSeek AI."},
                    {"id": 6, "type": "button", "text": "Get Started"}
                ]
            }
        }
        self.current_dom = []

    def navigate(self, url):
        print(f"\n[Browser] Navigating to: {url}")
        if url in self.pages:
            self.current_url = url
            self.current_dom = self.pages[url]["elements"]
            return True
        else:
            print(f"[Browser] 404 Not Found: {url}")
            return False

    def get_state(self):
        """Returns a simplified Accessibility Tree representation."""
        state = f"URL: {self.current_url}\nTitle: {self.pages.get(self.current_url, {}).get('title', 'Unknown')}\nInteractive Elements:\n"
        for el in self.current_dom:
            if el["type"] == "input":
                state += f"[{el['id']}] Input (name={el.get('name')}, value='{el.get('value')}')\n"
            elif el["type"] == "button":
                state += f"[{el['id']}] Button (text='{el.get('text')}')\n"
            elif el["type"] == "link":
                state += f"[{el['id']}] Link (text='{el.get('text')}')\n"
            elif el["type"] == "text":
                state += f"    Text: {el.get('content')}\n"
        return state

    def type_text(self, element_id, text):
        print(f"[Browser] Typing '{text}' into Element [{element_id}]")
        for el in self.current_dom:
            if el["id"] == element_id and el["type"] == "input":
                el["value"] = text
                return True
        return False

    def click(self, element_id):
        print(f"[Browser] Clicking Element [{element_id}]")
        # Logic to handle transitions based on clicks
        element = next((el for el in self.current_dom if el["id"] == element_id), None)
        if not element:
            return False

        if self.current_url == "https://www.google.com":
            if element["name"] == "btnK":
                # Check if input has value
                search_input = next((el for el in self.current_dom if el["name"] == "q"), None)
                if search_input and search_input["value"] == "DeepSeek":
                    self.navigate("https://www.google.com/search?q=DeepSeek")
                    return True

        elif self.current_url == "https://www.google.com/search?q=DeepSeek":
            if "href" in element:
                self.navigate(element["href"])
                return True

        return True

class MockLLM:
    """
    Simulates the AI Agent reasoning.
    In a real scenario, this would be GPT-4o receiving the state string.
    Here, we use rule-based logic to mimic the 'thought process'.
    """
    def generate_action(self, state, task):
        print(f"\n[LLM] Thinking... (Task: {task})")

        # Parse state to understand context
        url_match = re.search(r"URL: (.*)", state)
        current_url = url_match.group(1) if url_match else ""

        # Rule 1: If on Google and search box is empty, type 'DeepSeek'
        if "google.com" in current_url and "search?q" not in current_url:
            if "value=''" in state: # Input empty
                return {"action": "type", "element_id": 1, "text": "DeepSeek"}
            # Rule 2: If on Google and search box has 'DeepSeek', click Search
            elif "value='DeepSeek'" in state:
                return {"action": "click", "element_id": 2}

        # Rule 3: If on Results page, click the official link
        if "search?q=DeepSeek" in current_url:
             return {"action": "click", "element_id": 3} # Click DeepSeek link

        # Rule 4: If on DeepSeek page, we are done
        if "deepseek.com" in current_url and "google" not in current_url:
             return {"action": "done", "reason": "Navigated to DeepSeek homepage successfully."}

        return {"action": "fail", "reason": "No valid action found."}

class Agent:
    def __init__(self, task):
        self.task = task
        self.browser = MockBrowser()
        self.llm = MockLLM()

    def run(self):
        print(f"--- Starting Agent Task: {self.task} ---")
        self.browser.navigate("https://www.google.com")

        step = 0
        max_steps = 10

        while step < max_steps:
            step += 1
            print(f"\n--- Step {step} ---")

            # 1. Observe
            state = self.browser.get_state()
            print(f"[Observation]:\n{state.strip()}")

            # 2. Think
            action = self.llm.generate_action(state, self.task)
            print(f"[Decision]: {json.dumps(action)}")

            # 3. Act
            if action["action"] == "type":
                self.browser.type_text(action["element_id"], action["text"])
            elif action["action"] == "click":
                self.browser.click(action["element_id"])
            elif action["action"] == "done":
                print(f"\n[Success] {action['reason']}")
                break
            elif action["action"] == "fail":
                print(f"\n[Failure] {action['reason']}")
                break

            time.sleep(1) # Simulate network/processing delay

if __name__ == "__main__":
    agent = Agent("Go to DeepSeek homepage")
    agent.run()
