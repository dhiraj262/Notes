import re
import sys
import io
import contextlib

class MockLLM:
    """
    Simulates an LLM that is trained to write Python code to solve problems.
    In a real scenario, this would call an API like OpenAI or Anthropic.
    """
    def generate(self, prompt: str) -> str:
        # Heuristic response generation for the simulation
        if "fibonacci" in prompt.lower():
            return """
I will solve this by writing a Python script.

```python
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Calculate 10th fibonacci number
# 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55 (if 0 is 0th)
# Let's assume standard F(10) = 55
fib_10 = fibonacci(10)

# Multiply by 2 as requested
result = fib_10 * 2

print(f"The 10th Fibonacci number multiplied by 2 is: {result}")
final_answer = result
```
"""
        elif "search" in prompt.lower():
            return """
I will use the search tool to find the answer.

```python
# Search for the query
search_result = search_tool("current python version")
print(f"Search found: {search_result}")
final_answer = search_result
```
"""
        return "I don't know how to solve this."

class CodeAgent:
    """
    A simplified version of the SmolAgents CodeAgent.
    It takes an LLM and a set of tools, and executes the generated code.
    """
    def __init__(self, llm, tools=None):
        self.llm = llm
        self.tools = tools if tools else {}
        self.local_scope = {**self.tools} # Inject tools into the scope

    def run(self, task: str):
        print(f"🤖 Agent received task: {task}")

        # 1. Generate Code
        response = self.llm.generate(task)
        print(f"📝 LLM Generated Response:\n{'-'*20}\n{response}\n{'-'*20}")

        # 2. Extract Code
        code = self._extract_code(response)
        if not code:
            print("❌ No code block found in response.")
            return None

        print(f"💻 Extracted Code:\n{'-'*20}\n{code}\n{'-'*20}")

        # 3. Execute Code in Sandbox (Simulated)
        print("⚙️ Executing code in sandbox...")
        try:
            # Capture stdout
            output_capture = io.StringIO()
            with contextlib.redirect_stdout(output_capture):
                # Execute in the local_scope
                # Note: In a real agent, this would be a secure container (E2B/Docker)
                # 'final_answer' is a convention to extract the result
                # We use local_scope for both globals and locals to support recursion/function lookup
                exec(code, self.local_scope, self.local_scope)

            output = output_capture.getvalue()
            print(f"📤 Execution Output:\n{output}")

            # Check for a 'final_answer' variable which is a common pattern
            result = self.local_scope.get('final_answer')
            print(f"✅ Final Result: {result}")
            return result

        except Exception as e:
            print(f"❌ Execution Error: {e}")
            return None

    def _extract_code(self, response: str) -> str:
        # Regex to find code inside ```python ... ``` blocks
        match = re.search(r"```python(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

# --- Mock Tools ---
def search_tool(query):
    return f"Results for '{query}': Python 3.12 is the latest stable version."

# --- Main Simulation ---
if __name__ == "__main__":
    print("🚀 Starting SmolAgents Simulation (Code Agent Pattern)\n")

    # Initialize
    llm = MockLLM()
    tools = {"search_tool": search_tool}
    agent = CodeAgent(llm, tools)

    # Test Case 1: Computation
    print("\n--- Test Case 1: Pure Computation ---")
    agent.run("Calculate the 10th fibonacci number and multiply it by 2.")

    # Test Case 2: Tool Use
    print("\n--- Test Case 2: Tool Usage ---")
    agent.run("Search for the current python version.")
