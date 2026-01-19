import os
import time

class Agent:
    def __init__(self, name):
        self.name = name
        self.memory = []
        self.filesystem = {}  # Mock filesystem

    def log(self, message):
        print(f"[{self.name}] {message}")

    def write_file(self, filename, content):
        self.log(f"Attempting to write file: {filename}")
        # Hook for skills to intercept
        if not SkillRegistry.validate_action("write_file", self, filename=filename, content=content):
            self.log(f"❌ BLOCKED: Skill prevented writing {filename}")
            return False

        self.filesystem[filename] = content
        self.log(f"✅ SUCCESS: Wrote {filename}")
        return True

    def run_test(self, test_filename):
        self.log(f"Running test: {test_filename}")
        if test_filename not in self.filesystem:
            self.log(f"❌ Error: Test file {test_filename} not found")
            return False

        # Simple mock: if content contains "fail", it fails. Else passes.
        content = self.filesystem[test_filename]
        if "assert False" in content:
            self.log(f"❌ Test Failed: {test_filename}")
            return False

        self.log(f"✅ Test Passed: {test_filename}")
        return True

class SkillRegistry:
    skills = []

    @classmethod
    def register(cls, skill):
        cls.skills.append(skill)

    @classmethod
    def validate_action(cls, action_type, agent, **kwargs):
        for skill in cls.skills:
            if not skill.allow_action(action_type, agent, **kwargs):
                return False
        return True

class Skill:
    def allow_action(self, action_type, agent, **kwargs):
        return True

class TDDSkill(Skill):
    """
    Enforces Test-Driven Development.
    Rule: You cannot write implementation code (non-test files) unless a corresponding test file exists.
    """
    def allow_action(self, action_type, agent, **kwargs):
        if action_type == "write_file":
            filename = kwargs.get("filename")

            # Allow writing tests
            if filename.startswith("test_") or filename.endswith("_test.py"):
                return True

            # For implementation code, check if test exists
            test_filename = f"test_{filename}"
            if test_filename not in agent.filesystem:
                print(f"[TDDSkill] ✋ WAIT! You are trying to write implementation '{filename}' but '{test_filename}' does not exist.")
                print(f"[TDDSkill] ⚠️  Mandatory Rule: Write the failing test first.")
                return False

            print(f"[TDDSkill] ✅ Test file '{test_filename}' found. Proceeding with implementation.")
            return True
        return True

def run_simulation():
    print("🚀 Starting Superpowers TDD Simulation")
    print("---------------------------------------")

    # 1. Setup
    agent = Agent("Claude-Dev")
    tdd_skill = TDDSkill()
    SkillRegistry.register(tdd_skill)

    # 2. Scenario: User asks for 'calculator.py'
    print("\n📝 Scenario: User asks to implement 'calculator.py'")

    # 3. Agent tries to write implementation first (The "Junior" mistake)
    print("\n--- Step 1: Agent tries to write implementation first ---")
    success = agent.write_file("calculator.py", "def add(a, b): return a + b")
    if not success:
        print("(Simulation: Agent realizes it must write a test first)")

    # 4. Agent writes the test (RED)
    print("\n--- Step 2: Agent writes the test (RED) ---")
    agent.write_file("test_calculator.py", "def test_add(): assert True # Placeholder")

    # 5. Agent tries implementation again
    print("\n--- Step 3: Agent tries implementation again ---")
    success = agent.write_file("calculator.py", "def add(a, b): return a + b")

    # 6. Run verification
    if success:
        print("\n--- Step 4: Verification ---")
        agent.run_test("test_calculator.py")

    print("\n---------------------------------------")
    print("🏁 Simulation Complete. The framework successfully enforced TDD.")

if __name__ == "__main__":
    run_simulation()
