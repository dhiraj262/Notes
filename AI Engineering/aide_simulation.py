import random
import math
import heapq

class Solution:
    def __init__(self, code, parent=None, improvement_desc=""):
        self.code = code  # In this sim, 'code' is a list of hyperparameters [x, y]
        self.score = float('-inf')
        self.parent = parent
        self.improvement_desc = improvement_desc
        self.children = []

    def __repr__(self):
        return f"Solution(code={self.code}, score={self.score:.4f})"

class Evaluator:
    """
    Simulates the evaluation step.
    Goal: Maximize the function f(x, y) = -((x-10)^2 + (y-5)^2)
    Peak is at (10, 5) with score 0.
    """
    def evaluate(self, solution):
        x, y = solution.code
        # Simple quadratic objective function (negative distance to target)
        score = -((x - 10)**2 + (y - 5)**2)
        solution.score = score
        return score

class CodingOperator:
    """
    Simulates the LLM Coding Operator.
    It takes a solution and 'improves' it by tweaking values.
    """
    def propose_improvement(self, solution):
        # Simulate LLM drafting/improving code
        # We perturb the current values slightly (local search behavior)
        if solution is None:
            # Initial draft (random start)
            return [random.uniform(0, 20), random.uniform(0, 20)]

        current_code = solution.code
        new_code = [
            current_code[0] + random.uniform(-2, 2),
            current_code[1] + random.uniform(-2, 2)
        ]
        return new_code

class AIDE:
    """
    AI-Driven Exploration Agent.
    Implements the Tree Search algorithm.
    """
    def __init__(self, steps=20):
        self.steps = steps
        self.evaluator = Evaluator()
        self.coding_operator = CodingOperator()
        self.root = None
        self.solutions = [] # Flat list for tracking

    def run(self):
        print(f"--- Starting AIDE Simulation (Steps: {self.steps}) ---")

        # Step 1: Initialize Base Solution (Drafting)
        initial_code = self.coding_operator.propose_improvement(None)
        self.root = Solution(initial_code, improvement_desc="Initial Draft")
        self.evaluator.evaluate(self.root)
        self.solutions.append(self.root)

        print(f"Step 0: Initial Draft -> {self.root}")

        current_best = self.root

        for i in range(1, self.steps + 1):
            # Step 2: Search Policy (Select best node to expand)
            # AIDE uses a policy pi(T). Simple version: Greedy Best-First
            # We filter for nodes that haven't been over-expanded or we just pick the global best
            # and try to improve it (hill climbing with history).

            # In this sim, we pick the current best solution to improve
            base_solution = max(self.solutions, key=lambda s: s.score)

            # Step 3: Coding Operator (Propose new solution)
            new_code = self.coding_operator.propose_improvement(base_solution)

            # Step 4: Evaluate
            new_solution = Solution(new_code, parent=base_solution, improvement_desc=f"Step {i} Improvement")
            self.evaluator.evaluate(new_solution)

            # Update Tree
            base_solution.children.append(new_solution)
            self.solutions.append(new_solution)

            print(f"Step {i}: Improving {base_solution.code} -> {new_solution}")

            if new_solution.score > current_best.score:
                current_best = new_solution
                print(f"  >>> New Best Found! Score: {current_best.score:.4f}")

        return current_best

if __name__ == "__main__":
    # Fix seed for reproducibility
    random.seed(42)

    aide_agent = AIDE(steps=15)
    best_result = aide_agent.run()

    print("\n--- Final Result ---")
    print(f"Best Solution Found: {best_result.code}")
    print(f"Target Solution: [10, 5]")
    print(f"Final Score: {best_result.score:.4f}")
