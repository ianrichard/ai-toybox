import asyncio
import sys
import os
import json  # Import json for history serialization
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from typing import AsyncGenerator, Optional, Dict, Any, Callable, Union

load_dotenv()  # Load environment variables from .env

class AgentService:
    """Core service layer for agent interactions that can be used by multiple frontends."""
    
    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        model_name = os.getenv("BASE_MODEL", "default-model-name")  # Provide a default model name
        if not model_name:
            raise ValueError("BASE_MODEL environment variable is not set or invalid.")
        
        self.agent = Agent(
            model_name,            
            mcp_servers=[MCPServerStdio(sys.executable, args=["mcp_server.py"])],
            system_prompt=system_prompt,
        )
        
    async def __aenter__(self):
        """Start MCP servers when used as context manager."""
        self._mcp_context = self.agent.run_mcp_servers()
        await self._mcp_context.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop MCP servers when exiting context."""
        await self._mcp_context.__aexit__(exc_type, exc_val, exc_tb)
    
    async def process_input(self, user_input: str, 
                            history: Optional[list] = None,
                            on_assistant_message: Optional[Callable] = None,
                            on_tool_call: Optional[Callable] = None,
                            on_tool_result: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Process user input and handle the agent response.
        """
        response = {
            "assistant_content": "",
            "tool_calls": [],
            "tool_results": []
        }
        
        try:
            # Combine history and user input if necessary
            if history:
                user_input = f"History: {json.dumps(history)}\nUser: {user_input}"
            
            print(f"Processing input: {user_input}")  # Debug log
            async with self.agent.iter(user_input) as run:
                async for node in run:
                    print(f"Processing node: {node}")  # Debug log
                    if Agent.is_model_request_node(node):
                        async with node.stream(run.ctx) as stream:
                            collected_content = ""
                            async for event in stream:
                                print(f"Model event: {event}")  # Debug log
                                if hasattr(event, 'delta') and hasattr(event.delta, 'content_delta'):
                                    delta = event.delta.content_delta
                                    if delta:
                                        collected_content += delta
                                        if on_assistant_message:
                                            on_assistant_message(delta)
                        
                        response["assistant_content"] = collected_content
                                
                    elif Agent.is_call_tools_node(node):
                        async with node.stream(run.ctx) as stream:
                            async for event in stream:
                                print(f"Tool event: {event}")  # Debug log
                                if hasattr(event, 'part') and hasattr(event.part, 'tool_name'):
                                    if event.part.args and event.part.args.strip() not in ["", "{}"]:
                                        tool_call = {
                                            "tool_name": event.part.tool_name,
                                            "args": event.part.args
                                        }
                                        response["tool_calls"].append(tool_call)
                                        if on_tool_call:
                                            on_tool_call(tool_call)
                                
                                elif hasattr(event, 'result') and hasattr(event.result, 'content'):
                                    result = event.result.content.content[0].text
                                    response["tool_results"].append(result)
                                    if on_tool_result:
                                        on_tool_result(result)
        
        except Exception as e:
            print(f"Error in process_input: {e}")  # Debug log
            response["error"] = str(e)
            raise  # Optionally re-raise the exception
            
        return response