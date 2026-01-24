import re
import sys
import io
from typing import Dict, Any, Callable

# --- 1. Mock Tools ---
def get_weather(city: str) -> int:
    """Mock tool to get weather (returns integer F)."""
    print(f"    [System] Tool 'get_weather' called for {city}...")
    if "New York" in city:
        return 75
    return 0

# --- 2. Mock LLM ---
class MockLLM:
    """
    Simulates an LLM that knows how to write Python code for specific prompts.
    In a real scenario, this would call an API like OpenAI or Anthropic.
    """
    def generate(self, prompt: str) -> str:
        # Simple rule-based logic to simulate 'intelligence' for this demo

        # Step 3: Agent sees the Celsius value and concludes
        if "The temperature in Celsius is 23.89" in prompt:
            return "Final Answer: The temperature in New York is roughly 23.89 degrees Celsius."

        # Step 2: Agent sees the Observation (75) and needs to convert
        elif "Current temperature in F: 75" in prompt:
             return """
The weather is 75F. Now I will convert this value to Celsius using the formula (F - 32) * 5/9.

```python
# Step 2: Convert to Celsius
fahrenheit = 75
celsius = (fahrenheit - 32) * 5/9
print(f"The temperature in Celsius is {celsius:.2f}")
```
"""

        # Step 1: User asks for weather (and we haven't started yet)
        elif "weather in New York" in prompt:
            return """
I need to check the weather in New York first. I will use the `get_weather` tool.
Then I will convert it to Celsius.

```python
# Step 1: Get the weather
fahrenheit = get_weather("New York")
print(f"Current temperature in F: {fahrenheit}")
```
"""

        else:
            return "I am not sure what to do. Final Answer: Unknown."

# --- 3. Code Agent ---
class CodeAgent:
    def __init__(self, tools: Dict[str, Callable], llm: MockLLM):
        self.tools = tools
        self.llm = llm
        self.history = ""
        # Persistent scope for the agent's session (optional, but good for multi-turn)
        self.session_locals = {}

    def run(self, task: str):
        print(f"--- Starting Task: {task} ---")
        self.history += f"Task: {task}\n"

        max_turns = 3
        for i in range(max_turns):
            print(f"\n--- Turn {i+1} ---")

            # 1. Generate Thought & Action
            response = self.llm.generate(self.history)
            print(f"[Agent]: {response}")
            self.history += response + "\n"

            # 2. Check for Code
            code_match = re.search(r"```python(.*?)```", response, re.DOTALL)
            if not code_match:
                if "Final Answer" in response:
                    print("\n--- Task Complete ---")
                    return
                print("[System] No code found in response.")
                break

            code = code_match.group(1).strip()

            # 3. Execute Code
            print(f"[System] Executing Code Block...")
            output = self.execute_code(code)
            print(f"[System] Output: {output}")

            # 4. Update History with Observation
            self.history += f"Observation: {output}\n"

    def execute_code(self, code: str) -> str:
        """
        Executes the provided Python code in a controlled environment.
        Captures stdout as the 'Observation'.
        """
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        # Prepare execution environment
        # We pass the tools as globals so the code can call them.
        # We use a persistent locals dict if we want variables to survive between turns (CodeAct style)
        # But for this simple mock, per-block execution with shared tools is sufficient.

        global_scope = self.tools.copy()
        # Add 'print' to globals if needed, though it's built-in.

        try:
            # We use the same dict for globals and locals to allow functions to see themselves
            # and to simplify scope, similar to how REPLs often work.
            exec(code, global_scope, global_scope)
            result = redirected_output.getvalue().strip()
            if not result:
                result = "(No output)"
        except Exception as e:
            result = f"Error during execution: {e}"
        finally:
            sys.stdout = old_stdout

        return result

# --- 4. Main Execution ---
if __name__ == "__main__":
    print("Initializing Smolagents Simulation (Code Agents)...")

    # Define available tools
    tools = {
        "get_weather": get_weather
    }

    # Initialize components
    mock_llm = MockLLM()
    agent = CodeAgent(tools, mock_llm)

    # Run a task
    agent.run("What is the weather in New York in Celsius?")
