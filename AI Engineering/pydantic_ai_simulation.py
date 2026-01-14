import asyncio
import json
from typing import List, Optional, Generic, TypeVar, Any
from pydantic import BaseModel, Field, ValidationError
from dataclasses import dataclass

# ==========================================
# PART 1: The Simulation Framework
# (Mocking the core behavior of PydanticAI)
# ==========================================

T = TypeVar("T")

@dataclass
class RunContext(Generic[T]):
    """
    Simulates PydanticAI's RunContext.
    It wraps dependencies (deps) that are injected at runtime.
    This allows tools to access DBs, APIs, etc. in a type-safe way.
    """
    deps: T

class Agent:
    def __init__(self, system_prompt: str, result_type: type[BaseModel]):
        self.system_prompt = system_prompt
        self.result_type = result_type

    async def run(self, user_prompt: str, deps: Any) -> BaseModel:
        """
        Simulates the Agent execution loop:
        1. Context Injection
        2. LLM Call (Mocked)
        3. Validation
        """
        # Create the context wrapper
        ctx = RunContext(deps=deps)

        print(f"\n[Agent] 🤖 Starting run...")
        print(f"[Agent] 📝 User Prompt: '{user_prompt}'")
        print(f"[Agent] 💉 Injecting Dependencies: {deps}")

        # --- Simulate LLM Response (The "Intelligence") ---
        # In a real scenario, this comes from OpenAI/Anthropic.
        # Here we mock a response based on the prompt keywords to show validation logic.

        mock_llm_response_json = ""

        if "fail" in user_prompt.lower():
            # Simulate a hallucination/bad format (Price is a string, missing flight_id)
            print("[LLM] 💭 Generating malformed response to test validation...")
            mock_llm_response_json = '{"price": "expensive", "currency": "USD"}'
        else:
            # Simulate a perfect response
            print("[LLM] 💭 Generating valid structured response...")
            mock_llm_response_json = json.dumps({
                "flight_id": "AA-1092",
                "price": 450.50,
                "currency": "USD",
                "confirmed": True,
                "passenger_tier": deps.get_user_tier(1) # Simulating that the LLM used the tool/context
            })

        print(f"[LLM] 📤 Raw JSON Output: {mock_llm_response_json}")

        try:
            # --- The Core Magic: Pydantic Validation ---
            # This is what PydanticAI does: enforces the schema on the raw string.
            result = self.result_type.model_validate_json(mock_llm_response_json)
            print(f"[Validation] ✅ Success! Object type: {type(result).__name__}")
            return result
        except ValidationError as e:
            print(f"[Validation] ❌ FAILED. The LLM output did not match the schema.")
            print(f"--- Error Details ---\n{e}\n---------------------")
            print("[Agent] 🔄 In a real PydanticAI app, I would now send this error back to the LLM to auto-correct.")
            raise

# ==========================================
# PART 2: User Code
# (How a developer uses the framework)
# ==========================================

# 1. Define Dependencies (The "Context")
@dataclass
class DatabaseConn:
    db_url: str
    active: bool

    def get_user_tier(self, user_id: int) -> str:
        # Mock database lookup
        return "Platinum" if user_id == 1 else "Gold"

# 2. Define Output Schema (The "Contract")
class BookingResult(BaseModel):
    flight_id: str = Field(description="The airline flight code")
    price: float = Field(description="Ticket price")
    currency: str = Field(default="USD")
    confirmed: bool = Field(description="Whether the booking is confirmed")
    passenger_tier: str = Field(description="The tier of the passenger used for pricing")

# 3. Initialize Agent
agent = Agent(
    system_prompt="You are a travel booking assistant. You must return a valid BookingResult.",
    result_type=BookingResult
)

# ==========================================
# PART 3: Execution
# ==========================================

async def main():
    # Setup the dependency
    db = DatabaseConn(db_url="postgres://production:5432", active=True)

    print("==============================================")
    print("SCENARIO 1: The Happy Path")
    print("==============================================")
    try:
        result = await agent.run("Book me a flight to NYC (User ID 1)", deps=db)
        print(f"\nFinal Result Object:\n{result}")
        print(f"Accessed Field safely: {result.price} (Type: {type(result.price)})")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("\n\n==============================================")
    print("SCENARIO 2: The Validation Failure")
    print("==============================================")
    try:
        await agent.run("Please fail this request to test error handling", deps=db)
    except ValidationError:
        print("\n[System] Caught expected validation error. The application is safe.")

if __name__ == "__main__":
    asyncio.run(main())
