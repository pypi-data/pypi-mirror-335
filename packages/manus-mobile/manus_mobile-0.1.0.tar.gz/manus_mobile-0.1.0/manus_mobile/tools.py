"""
Tool providers and utilities for manus_mobile
"""

from typing import Dict, Any, List
from .adb_client import ADBClient

class MobileToolProvider:
    """Provider for mobile automation tools."""
    
    def __init__(self, adb_client: ADBClient):
        """Initialize with an ADB client."""
        self.adb_client = adb_client
        self.tools = {}
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up the available tools."""
        # Open app tool
        self.tools["open_app"] = {
            "name": "open_app",
            "description": "Open an app on android device.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "package name of the app to open such as com.google.android.dialer"
                    }
                },
                "required": ["name"]
            },
            "function": self._open_app
        }
        
        # Add more tools as needed
    
    async def _open_app(self, name: str) -> str:
        """Open the specified app by package name."""
        await self.adb_client.openApp(name)
        return f"Successfully opened {name}"
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get tools description for LLM."""
        tools = []
        for tool_name, tool_info in self.tools.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                }
            })
        return tools

    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool with the given arguments."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        
        try:
            result = await self.tools[tool_name]["function"](**kwargs)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}" 