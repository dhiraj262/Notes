import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, TypeVar, Optional, get_type_hints

# --- 1. The PydanticAI Framework Simulation (Under the Hood) ---

DepsT = TypeVar("DepsT")

@dataclass
class RunContext(Generic[DepsT]):
    """
    Simulates PydanticAI's RunContext.
    It wraps the dependencies injected at runtime.
    """
    deps: DepsT
    retry: int = 0
    tool_name: Optional[str] = None

class Agent(Generic[DepsT]):
    """
    A simplified reconstruction of the PydanticAI Agent class.
    Demonstrates:
    1. Tool Registration
    2. Dependency Injection (DI) during execution
    3. Type-Safe Tool Calling
    """
    def __init__(self, system_prompt: str, deps_type: type[DepsT]):
        self.system_prompt = system_prompt
        self.deps_type = deps_type
        self.tools: Dict[str, Callable] = {}

    def tool(self, func: Callable) -> Callable:
        """Decorator to register a tool."""
        self.tools[func.__name__] = func
        return func

    def run(self, user_prompt: str, deps: DepsT) -> str:
        """
        Simulates the agent 'run' loop.
        In a real scenario, this would send schemas to an LLM.
        Here, we mock the LLM's decision making to demonstrate DI.
        """
        print(f"\n--- 🤖 Agent Running: {user_prompt} ---")

        # 1. Create the RunContext with the provided dependencies
        ctx = RunContext(deps=deps)

        # 2. Mock LLM Logic: Decide which tool to call based on the prompt
        # (This is hardcoded for simulation purposes to show the *mechanics* working)
        if "balance" in user_prompt.lower():
            tool_name = "get_balance"
            tool_args = {}
        elif "transfer" in user_prompt.lower():
            tool_name = "transfer_money"
            # Extract mock amount
            import re
            match = re.search(r'\$(\d+(\.\d+)?)', user_prompt)
            amount = float(match.group(1)) if match else 100.0
            tool_args = {"amount": amount, "to_user": "Alice"}
        else:
            return "I don't know how to do that."

        # 3. Execute the tool with Dependency Injection
        if tool_name in self.tools:
            return self._execute_tool(tool_name, tool_args, ctx)

        return "Tool not found."

    def _execute_tool(self, tool_name: str, args: Dict[str, Any], ctx: RunContext[DepsT]) -> str:
        """
        The Core DI Logic:
        Inspects the tool's type hints. If 'RunContext' is found, injects it.
        """
        func = self.tools[tool_name]
        type_hints = get_type_hints(func)

        # Prepare arguments for the function call
        call_args = {}

        print(f"   [System] Inspecting tool '{tool_name}' signature...")

        # Iterate over function parameters to find where to inject context
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            # Check if the parameter expects RunContext
            # Note: In a robust system, we'd check the generic type too
            param_type = type_hints.get(param_name)

            if param_type and hasattr(param_type, "__origin__") and param_type.__origin__ is RunContext:
                print(f"   [DI] Injecting RunContext into parameter '{param_name}'")
                call_args[param_name] = ctx
            elif param_name in args:
                call_args[param_name] = args[param_name]

        # Call the function
        result = func(**call_args)
        return f"Tool Output: {result}"

# --- 2. The User Implementation (How a developer uses PydanticAI) ---

# Define our dependencies (e.g., Database Connection)
@dataclass
class BankDatabase:
    db_url: str
    user_id: int
    _balances: Dict[int, float]

    def get_balance(self) -> float:
        return self._balances.get(self.user_id, 0.0)

    def deduct(self, amount: float):
        if self._balances[self.user_id] >= amount:
            self._balances[self.user_id] -= amount
            return True
        return False

# Initialize Agent
agent = Agent(
    system_prompt="You are a helpful banking assistant.",
    deps_type=BankDatabase
)

# Define Tools using the agent decorator
@agent.tool
def get_balance(ctx: RunContext[BankDatabase]) -> str:
    """Check the user's balance."""
    # Access dependencies via ctx.deps
    balance = ctx.deps.get_balance()
    return f"Current balance is ${balance:.2f} (Database: {ctx.deps.db_url})"

@agent.tool
def transfer_money(ctx: RunContext[BankDatabase], amount: float, to_user: str) -> str:
    """Transfer money to another user."""
    # Access dependencies via ctx.deps
    success = ctx.deps.deduct(amount)
    if success:
        return f"Successfully transferred ${amount} to {to_user}. Remaining: ${ctx.deps.get_balance()}"
    else:
        return "Insufficient funds."

# --- 3. Execution / Simulation ---

if __name__ == "__main__":
    # Setup the runtime dependency (e.g., for User 123)
    mock_db = BankDatabase(
        db_url="postgres://prod-db:5432",
        user_id=123,
        _balances={123: 1000.0}
    )

    print("--- Simulation Start ---")

    # Run 1: Check Balance
    # The 'run' method will mock the LLM choosing 'get_balance'
    # The '_execute_tool' method will inject 'mock_db' wrapped in RunContext
    response1 = agent.run("Check my balance", deps=mock_db)
    print(f"Agent Response: {response1}")

    # Run 2: Transfer Money
    # The 'run' method will mock the LLM choosing 'transfer_money'
    response2 = agent.run("Transfer $200 to Alice", deps=mock_db)
    print(f"Agent Response: {response2}")

    # Verify State Change
    print(f"\n[Verification] Final DB Balance: ${mock_db.get_balance()}")
