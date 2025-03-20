"""
Core functionality for manus_mobile
"""

from typing import Dict, Any, Optional, Callable
import asyncio

from .adb_client import ADBClient
from .mobile_computer import create_mobile_computer
from .tools import MobileToolProvider

# Default system prompt for mobile automation
MOBILE_USE_PROMPT = """You are an experienced mobile automation engineer. 
Your job is to navigate an android device and perform actions to fulfill request of the user.

<steps>
If the user asks to use a specific app in the request, open it before performing any other action.
Do not take ui dump more than once per action. If you think you don't need to take ui dump, skip it. Use it sparingly.
</steps>
"""

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