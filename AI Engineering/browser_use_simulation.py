import time
import json
import re

class MockBrowser:
    """
    Simulates a Headless Browser (like Playwright).
    It manages a virtual DOM and allows navigation and interaction.
    """
    def __init__(self):
        self.current_url = "about:blank"
        self.last_typed_search = ""
        # simulated_web_pages maps URL -> Content
        self.simulated_web_pages = {
            "https://www.shop-ai.com": {
                "title": "Shop AI - Home",
                "elements": [
                    {"id": 1, "type": "input", "name": "search", "placeholder": "Search products..."},
                    {"id": 2, "type": "button", "text": "Search", "action": "submit_search"},
                ]
            },
            "https://www.shop-ai.com/search?q=laptop": {
                "title": "Search Results - Laptop",
                "elements": [
                    {"id": 3, "type": "link", "text": "SuperFast Laptop X1 - $999", "href": "/product/laptop-x1"},
                    {"id": 4, "type": "link", "text": "Budget ChromeBook - $299", "href": "/product/chromebook"},
                ]
            },
            "https://www.shop-ai.com/product/laptop-x1": {
                "title": "SuperFast Laptop X1",
                "elements": [
                    {"id": 5, "type": "text", "content": "Price: $999. In Stock."},
                    {"id": 6, "type": "button", "text": "Add to Cart", "action": "add_to_cart"},
                ]
            },
            "https://www.shop-ai.com/cart": {
                "title": "Your Cart",
                "elements": [
                    {"id": 7, "type": "text", "content": "1x SuperFast Laptop X1"},
                    {"id": 8, "type": "button", "text": "Checkout", "action": "checkout"},
                ]
            }
        }
        self.history = []
        self.cart = []

    def navigate(self, url):
        print(f"🌐 [Browser] Navigating to: {url}")
        if url in self.simulated_web_pages:
            self.current_url = url
            return True
        elif url.startswith("/"):
            # Handle relative paths
            base = "https://www.shop-ai.com"
            full_url = base + url
            if full_url in self.simulated_web_pages:
                self.current_url = full_url
                return True

        print(f"❌ [Browser] 404 Not Found: {url}")
        return False

    def get_state(self):
        """Returns the 'Accessibility Tree' (simplified DOM) for the LLM."""
        page = self.simulated_web_pages.get(self.current_url)
        if not page:
            return "Page not found."

        state_desc = f"URL: {self.current_url}\nTitle: {page['title']}\nInteractive Elements:\n"
        for el in page['elements']:
            if el['type'] == 'input':
                # Show value if typed
                value_str = f" [Value: '{self.last_typed_search}']" if el.get('name') == 'search' and self.last_typed_search else ""
                state_desc += f"[{el['id']}] Input: {el.get('placeholder', '')} (Name: {el.get('name')}){value_str}\n"
            elif el['type'] == 'button':
                state_desc += f"[{el['id']}] Button: {el.get('text')}\n"
            elif el['type'] == 'link':
                state_desc += f"[{el['id']}] Link: {el.get('text')}\n"
            elif el['type'] == 'text':
                state_desc += f"Text: {el.get('content')}\n"
        return state_desc

    def type_text(self, element_id, text):
        print(f"⌨️ [Browser] Typing '{text}' into Element [{element_id}]")
        # In a real browser, this would update the DOM value.
        # Here we just simulate the side effect if it's the search bar.
        page = self.simulated_web_pages[self.current_url]
        for el in page['elements']:
            if el['id'] == element_id and el.get('name') == 'search':
                self.last_typed_search = text
                return True
        return False

    def click(self, element_id):
        print(f"🖱️ [Browser] Clicking Element [{element_id}]")
        page = self.simulated_web_pages[self.current_url]
        for el in page['elements']:
            if el['id'] == element_id:
                if el['type'] == 'link':
                    return self.navigate(el['href'])
                elif el['type'] == 'button':
                    action = el.get('action')
                    if action == 'submit_search':
                        query = getattr(self, 'last_typed_search', 'laptop') # Default if not typed
                        return self.navigate(f"https://www.shop-ai.com/search?q={query}")
                    elif action == 'add_to_cart':
                        print("🛒 [Browser] Item added to cart!")
                        self.cart.append("Laptop X1")
                        return self.navigate("https://www.shop-ai.com/cart")
                    elif action == 'checkout':
                        print("🎉 [Browser] Checkout successful!")
                        return True
        return False

class MockLLM:
    """
    Simulates the Vision/Reasoning Model (e.g., GPT-4o).
    It receives the Browser State and decides the next action.
    """
    def generate_action(self, task, browser_state, history):
        """
        In a real scenario, this calls the OpenAI API.
        Here, we use simple heuristic rules to simulate 'intelligence'.
        """
        print("\n🧠 [LLM] Thinking...")

        last_action = history[-1]['action'] if history else None

        # 1. If we just typed, we should click search
        if last_action and last_action['action'] == 'type':
            match = re.search(r'\[(\d+)\] Button: Search', browser_state)
            if match:
                return {"action": "click", "id": int(match.group(1))}

        # 2. If we are at Start Page and haven't typed yet
        if "Shop AI - Home" in browser_state:
            if "Value: 'laptop'" not in browser_state: # Check if already typed by looking at state
                 match = re.search(r'\[(\d+)\] Input', browser_state)
                 if match:
                     return {"action": "type", "id": int(match.group(1)), "text": "laptop"}

        # 3. If on Search Results, click the Laptop X1
        if "Search Results" in browser_state:
            match = re.search(r'\[(\d+)\] Link: SuperFast Laptop X1', browser_state)
            if match:
                return {"action": "click", "id": int(match.group(1))}

        # 4. If on Product Page, Add to Cart
        if "SuperFast Laptop X1" in browser_state and "Add to Cart" in browser_state:
            match = re.search(r'\[(\d+)\] Button: Add to Cart', browser_state)
            if match:
                return {"action": "click", "id": int(match.group(1))}

        # 5. If in Cart, verify and Finish
        if "Your Cart" in browser_state:
            if "1x SuperFast Laptop X1" in browser_state:
                return {"action": "done", "result": "Successfully added Laptop X1 to cart."}

        return {"action": "error", "message": "I am confused."}

class Agent:
    def __init__(self, task):
        self.task = task
        self.browser = MockBrowser()
        self.llm = MockLLM()
        self.history = []

    def run(self):
        print(f"🤖 [Agent] Starting Task: {self.task}")
        # Initial navigation
        self.browser.navigate("https://www.shop-ai.com")

        for step in range(10): # Max 10 steps
            state = self.browser.get_state()
            print(f"\n--- Step {step + 1} ---")
            print(state.strip())

            # Ask LLM for next move
            action_response = self.llm.generate_action(self.task, state, self.history)

            print(f"⚡ [Action] {action_response}")
            self.history.append({"state": state, "action": action_response})

            if action_response['action'] == 'done':
                print(f"\n✅ Task Completed: {action_response['result']}")
                return

            elif action_response['action'] == 'type':
                self.browser.type_text(action_response['id'], action_response['text'])

            elif action_response['action'] == 'click':
                self.browser.click(action_response['id'])

            time.sleep(1) # Simulate network/processing delay

if __name__ == "__main__":
    agent = Agent(task="Go to Shop AI, find a laptop, and add it to cart.")
    agent.run()
