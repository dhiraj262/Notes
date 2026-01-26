"""
Flow Engineering Simulation (AlphaCodium Pattern)

This script simulates the AlphaCodium flow:
1. Problem Reflection
2. Test Generation
3. Code Generation
4. Execution & Iterative Repair

It mocks the LLM to demonstrate the *control flow* and *logic* without needing API keys.
"""

import time
import random

class MockLLM:
    """
    Simulates an LLM that improves its probability of success
    when provided with better context (reflection, tests).
    """
    def __init__(self):
        pass

    def generate(self, prompt, context=None):
        """
        Returns a simulated response based on the 'stage' of the prompt.
        """
        if "Reflect on this problem" in prompt:
            return "REFLECTION: The problem asks for a function that finds the longest palindrome. Edge cases: empty string, single char, no palindrome."

        if "Generate unit tests" in prompt:
            return ["assert solve('aba') == 'aba'", "assert solve('a') == 'a'", "assert solve('abc') == 'a'"]

        if "Write code" in prompt:
            # Simulate a buggy initial attempt
            return """
def solve(s):
    # Initial Attempt (Buggy)
    if not s: return ""
    return s[0] # Returns first char only
"""

        if "Fix the code" in prompt:
            # Simulate a fix
            return """
def solve(s):
    # Fixed Solution
    res = ""
    for i in range(len(s)):
        # (Simplified palindrome logic for simulation)
        pass
    return "aba" # Mocking correct return for the test case
"""
        return "Generic LLM Response"

class AlphaCodiumFlow:
    def __init__(self, problem_statement):
        self.problem = problem_statement
        self.llm = MockLLM()
        self.context = {} # The "State" of the flow

    def step_1_reflection(self):
        print("\n--- Step 1: Flow Analysis (Reflection) ---")
        prompt = f"Reflect on this problem: {self.problem}"
        reflection = self.llm.generate(prompt)
        self.context['reflection'] = reflection
        print(f"LLM Output: {reflection}")

    def step_2_generate_tests(self):
        print("\n--- Step 2: Generate Tests ---")
        prompt = f"Generate unit tests based on reflection: {self.context['reflection']}"
        tests = self.llm.generate(prompt)
        self.context['tests'] = tests
        print(f"Generated {len(tests)} tests: {tests}")

    def step_3_generate_solution(self):
        print("\n--- Step 3: Initial Code Generation ---")
        prompt = f"Write code for: {self.problem}. Keep reflection in mind."
        code = self.llm.generate(prompt)
        self.context['code'] = code
        print("Generated Code Snippet (Simulated)")

    def step_4_run_and_fix(self):
        print("\n--- Step 4: Run & Fix Loop (Iterative Repair) ---")
        # Simulate running tests
        # In a real app, we would use `exec()` or a sandboxed runner.

        max_retries = 3
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1}: Running tests...")

            # Simulate Test Execution Logic
            # The initial code (mocked above) is buggy.
            if "Initial Attempt" in self.context['code']:
                success = False
                error = "Test Failed: assert solve('aba') == 'aba' (Got 'a')"
                print(f"  > Tests FAILED: {error}")
            else:
                success = True
                print("  > Tests PASSED!")

            if success:
                print("Flow Complete: Solution Verified.")
                return self.context['code']

            # If failed, trigger the "Fix" step
            print("  > Triggering Self-Reflection & Fix...")
            fix_prompt = f"Fix the code based on error: {error}\nCode:\n{self.context['code']}"
            fixed_code = self.llm.generate(fix_prompt)
            self.context['code'] = fixed_code

        print("Flow Failed: Could not converge on a solution.")
        return None

    def run(self):
        print(f"Starting AlphaCodium Flow for problem: '{self.problem}'")
        self.step_1_reflection()
        self.step_2_generate_tests()
        self.step_3_generate_solution()
        final_code = self.step_4_run_and_fix()
        return final_code

if __name__ == "__main__":
    # Example Problem: Longest Palindromic Substring
    flow = AlphaCodiumFlow("Find the longest palindromic substring in a given string s.")
    result = flow.run()
