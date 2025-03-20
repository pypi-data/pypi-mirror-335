"""
manus_mobile - Python library for AI-driven mobile device automation
"""

# Import typing classes
from typing import List, Dict, Any, Optional, Callable

# Export main classes and functions
from .adb_client import ADBClient, Coordinate
from .core import mobile_use, MOBILE_USE_PROMPT
from .tools import MobileToolProvider

__version__ = "0.1.0"
__all__ = [
    "ADBClient", 
    "Coordinate", 
    "mobile_use", 
    "MobileToolProvider",
    "MOBILE_USE_PROMPT"
]

# Default system prompt for mobile automation
MOBILE_USE_PROMPT = """You are an experienced mobile automation engineer. 
Your job is to navigate an android device and perform actions to fulfill request of the user.

<steps>
If the user asks to use a specific app in the request, open it before performing any other action.
Do not take ui dump more than once per action. If you think you don't need to take ui dump, skip it. Use it sparingly.
</steps>
"""

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


async def mobile_use(
    task: str, 
    llm_function: Optional[Callable] = None, 
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use AI to automate mobile device interactions.
    
    Args:
        task: The task description for the AI to perform
        llm_function: Function to call the LLM (must accept messages and return response)
        system_prompt: Optional custom system prompt
        
    Returns:
        The result of the AI-driven mobile automation
    """
    # Initialize the ADB client
    adb_client = ADBClient()
    
    # Create the mobile computer tool
    computer = await create_mobile_computer(adb_client)
    
    # Create the tool provider
    tool_provider = MobileToolProvider(adb_client)
    
    # Use the provided system prompt or the default
    system_prompt = system_prompt or MOBILE_USE_PROMPT
    
    # Generate messages for the LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task}
    ]
    
    # If LLM function is provided, use it
    if llm_function:
        # You can adapt this to work with different LLM providers
        tools = tool_provider.get_tools_for_llm()
        response = await llm_function(messages, tools=tools)
        return response
    else:
        # Return a message that an LLM function is required
        return {
            "role": "assistant",
            "content": "To use manus_mobile, you need to provide an LLM function that can process the task."
        } 