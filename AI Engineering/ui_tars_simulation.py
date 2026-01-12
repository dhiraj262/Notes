import asyncio
from typing import List, Dict, Any

# --- Mock MCP Infrastructure ---

class MCPTool:
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func

    async def execute(self, **kwargs) -> Any:
        print(f"    [MCP Tool Exec] {self.name} called with {kwargs}")
        return await self.func(**kwargs)

class MCPServer:
    def __init__(self, name: str):
        self.name = name
        self.tools: Dict[str, MCPTool] = {}

    def register_tool(self, tool: MCPTool):
        self.tools[tool.name] = tool

    def get_tool_definitions(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self.tools.values()]

    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        return await self.tools[tool_name].execute(**kwargs)

# --- Mock UI-TARS Desktop Operators (The "Hands") ---

class UITarsDesktopServer(MCPServer):
    def __init__(self):
        super().__init__("ui-tars-desktop")
        # Simulating state
        self.current_app = "Desktop"
        self.screen_content = {
            "Desktop": ["Icon: Chrome", "Icon: VS Code", "Icon: Terminal"],
            "VS Code": ["Menu: File", "Menu: Settings", "Input: Search Settings", "Text: AutoSave"],
            "Chrome": ["UrlBar", "WebContent: Google Homepage"]
        }
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool(MCPTool(
            "computer_screenshot",
            "Takes a screenshot and returns a description of visible elements (simulated VLM output).",
            self.mock_screenshot
        ))
        self.register_tool(MCPTool(
            "computer_mouse_click",
            "Clicks on an element or coordinate.",
            self.mock_click
        ))
        self.register_tool(MCPTool(
            "computer_keyboard_type",
            "Types text into the focused element.",
            self.mock_type
        ))
        self.register_tool(MCPTool(
            "computer_open_app",
            "Opens an application by name.",
            self.mock_open_app
        ))

    async def mock_screenshot(self, **kwargs):
        # Simulate the VLM "seeing" the screen
        await asyncio.sleep(0.5) # Simulate latency
        elements = self.screen_content.get(self.current_app, [])
        return f"[VLM Vision Output] Visible content in {self.current_app}: {', '.join(elements)}"

    async def mock_click(self, target: str, **kwargs):
        await asyncio.sleep(0.2)
        print(f"    [Action] Clicked on '{target}'")
        return "Success"

    async def mock_type(self, text: str, **kwargs):
        await asyncio.sleep(0.2)
        print(f"    [Action] Typed '{text}'")
        return "Success"

    async def mock_open_app(self, app_name: str, **kwargs):
        await asyncio.sleep(1.0) # App launch takes time
        if app_name in self.screen_content:
            self.current_app = app_name
            print(f"    [Action] Launched {app_name}")
            return f"Opened {app_name}"
        else:
            return f"Error: App {app_name} not found"

# --- Mock Agent (The "Brain") ---

class AgentTars:
    def __init__(self, mcp_server: MCPServer):
        self.server = mcp_server
        self.memory = []

    async def think_and_act(self, goal: str):
        print(f"\n🤖 Agent Goal: {goal}")

        # Step 1: Discover Tools
        tools = self.server.get_tool_definitions()
        print(f"🔍 Discovered {len(tools)} tools from MCP server '{self.server.name}'")

        # Step 2: Planning (Simulated Chain of Thought)
        plan = self._simulate_planning(goal)

        # Step 3: Execution Loop
        for step in plan:
            print(f"\n🧠 Thought: {step['thought']}")
            tool_name = step['tool']
            args = step['args']

            # Call the tool via MCP
            result = await self.server.call_tool(tool_name, **args)
            print(f"✅ Result: {result}")
            self.memory.append({"step": step, "result": result})

    def _simulate_planning(self, goal: str) -> List[Dict[str, Any]]:
        # Hardcoded logic for the specific "Open VS Code and change settings" scenario
        # In a real agent, this comes from the LLM
        if "VS Code" in goal and "settings" in goal:
            return [
                {
                    "thought": "I need to see what's on the screen first to find VS Code.",
                    "tool": "computer_screenshot",
                    "args": {}
                },
                {
                    "thought": "I see the VS Code icon. I will open the application.",
                    "tool": "computer_open_app",
                    "args": {"app_name": "VS Code"}
                },
                {
                    "thought": "VS Code is open. I need to confirm the UI state.",
                    "tool": "computer_screenshot",
                    "args": {}
                },
                {
                    "thought": "I see the 'Menu: Settings'. I will click it.",
                    "tool": "computer_mouse_click",
                    "args": {"target": "Menu: Settings"}
                },
                {
                    "thought": "I need to search for the setting.",
                    "tool": "computer_keyboard_type",
                    "args": {"text": "AutoSave"}
                }
            ]
        return []

# --- Main Simulation ---

async def main():
    # 1. Setup the UI-TARS Desktop MCP Server
    server = UITarsDesktopServer()

    # 2. Initialize the Agent
    agent = AgentTars(server)

    # 3. Give the Agent a task
    # Task: "Open VS Code and search for AutoSave settings"
    await agent.think_and_act("Open VS Code and search for AutoSave settings")

if __name__ == "__main__":
    asyncio.run(main())
