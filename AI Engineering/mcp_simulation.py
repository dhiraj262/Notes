import asyncio
import json
import uuid
from typing import Callable, Dict, Any, List, Optional

# ==========================================
# 1. THE CORE PROTOCOL (JSON-RPC 2.0 simulation)
# ==========================================

class JSONRPCMessage:
    """Helper to structure JSON-RPC messages."""
    @staticmethod
    def request(method: str, params: Optional[Dict] = None, msg_id: str = None):
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": msg_id or str(uuid.uuid4())
        }

    @staticmethod
    def response(result: Any, msg_id: str):
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": msg_id
        }

    @staticmethod
    def error(code: int, message: str, msg_id: str):
        return {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": msg_id
        }

# ==========================================
# 2. THE SERVER (The Tool Provider)
# ==========================================

class MCPServer:
    """
    Simulates an MCP Server.
    In the real world, this runs as a separate process (e.g., connected via stdio).
    """
    def __init__(self, name: str):
        self.name = name
        self.tools: Dict[str, Callable] = {}
        # Resources could also be added here (e.g., file readers)

    def register_tool(self, name: str, description: str, func: Callable):
        self.tools[name] = {
            "description": description,
            "func": func
        }

    async def handle_message(self, message: Dict) -> Dict:
        """Process an incoming JSON-RPC message."""
        if "method" not in message:
            return JSONRPCMessage.error(-32600, "Invalid Request", message.get("id"))

        method = message["method"]
        msg_id = message.get("id")

        print(f"[{self.name}] Received Request: {method}")

        if method == "tools/list":
            # Standard MCP endpoint to list available tools
            tool_list = [
                {"name": name, "description": data["description"]}
                for name, data in self.tools.items()
            ]
            return JSONRPCMessage.response({"tools": tool_list}, msg_id)

        elif method == "tools/call":
            # Standard MCP endpoint to execute a tool
            params = message.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name not in self.tools:
                return JSONRPCMessage.error(-32601, f"Tool '{tool_name}' not found", msg_id)

            try:
                # Execute the actual python function
                func = self.tools[tool_name]["func"]
                result = func(**tool_args)
                return JSONRPCMessage.response({"content": [{"type": "text", "text": str(result)}]}, msg_id)
            except Exception as e:
                return JSONRPCMessage.error(-32000, str(e), msg_id)

        else:
            return JSONRPCMessage.error(-32601, "Method not found", msg_id)

# ==========================================
# 3. THE CLIENT (The Host / LLM Agent)
# ==========================================

class MCPClient:
    """
    Simulates an MCP Client (e.g., Claude Desktop, or an Agent).
    It connects to the server and sends requests.
    """
    def __init__(self, server: MCPServer):
        self.server = server

    async def send_request(self, method: str, params: Optional[Dict] = None):
        """Simulates sending a request over the wire (stdio/SSE)."""
        request = JSONRPCMessage.request(method, params)

        # Simulate Network Latency
        print(f"[Client] Sending JSON-RPC: {json.dumps(request)}")
        await asyncio.sleep(0.1)

        # In a real app, this is written to stdout/stdin
        response = await self.server.handle_message(request)

        print(f"[Client] Received JSON-RPC: {json.dumps(response)}")
        return response

    async def discover_and_use_tools(self, task_description: str):
        print(f"\n--- Starting Task: {task_description} ---")

        # 1. Handshake / Discovery
        print("\n[Step 1] Discovering Tools...")
        response = await self.send_request("tools/list")
        tools = response["result"]["tools"]
        print(f"Available Tools: {[t['name'] for t in tools]}")

        # 2. "LLM" Logic (Simulated)
        # We manually map the task to a tool call for this simulation
        if "weather" in task_description:
            print("\n[Step 2] LLM Decides: Call 'get_weather' tool")
            tool_name = "get_weather"
            args = {"city": "San Francisco"}
        elif "calculate" in task_description:
            print("\n[Step 2] LLM Decides: Call 'calculator' tool")
            tool_name = "calculator"
            args = {"a": 10, "b": 5, "op": "multiply"}
        else:
            print("No suitable tool found.")
            return

        # 3. Execution
        print(f"\n[Step 3] Executing {tool_name} with {args}...")
        call_response = await self.send_request("tools/call", {"name": tool_name, "arguments": args})

        result_text = call_response["result"]["content"][0]["text"]
        print(f"\n[Step 4] Final Result: {result_text}")

# ==========================================
# 4. ACTUAL IMPLEMENTATION OF TOOLS
# ==========================================

def get_weather(city: str) -> str:
    """A mock weather tool."""
    return f"The weather in {city} is Sunny, 25°C."

def calculator(a: int, b: int, op: str) -> int:
    """A mock calculator tool."""
    if op == "add": return a + b
    if op == "multiply": return a * b
    return 0

# ==========================================
# 5. MAIN EXECUTION
# ==========================================

async def main():
    # Setup Server
    server = MCPServer(name="Demo-MCP-Server")
    server.register_tool("get_weather", "Get current weather for a city", get_weather)
    server.register_tool("calculator", "Perform basic math", calculator)

    # Setup Client
    client = MCPClient(server)

    # Run Scenarios
    await client.discover_and_use_tools("Check the weather in San Francisco")

if __name__ == "__main__":
    asyncio.run(main())
