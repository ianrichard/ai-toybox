import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
import sys
from typing import Optional, List, Dict, Any, AsyncGenerator, Callable
from log_utils import log_msg, log_stream

class AgentHandler:
    """
    Core handler for agent interactions that can be used by terminal or API interfaces.
    """
    def __init__(
        self, 
        model: str = "openai:gpt-4o-mini",
        system_prompt: str = "You are a helpful assistant.",
        mcp_script: str = "mcp_server.py"
    ):
        self.agent = Agent(
            model,
            mcp_servers=[MCPServerStdio(sys.executable, args=[mcp_script])],
            system_prompt=system_prompt,
        )
        self.mcp_ready = False
        
    async def start_mcp(self):
        """Initialize and start the MCP server."""
        if not self.mcp_ready:
            self._mcp_context = self.agent.run_mcp_servers()
            await self._mcp_context.__aenter__()
            self.mcp_ready = True
            return True
        return False
            
    async def stop_mcp(self):
        """Properly shut down the MCP server."""
        if self.mcp_ready:
            await self._mcp_context.__aexit__(None, None, None)
            self.mcp_ready = False
            return True
        return False
    
    async def process_message(
        self, 
        message: str,
        on_assistant_stream: Callable = None,
        on_tool_stream: Callable = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return the response.
        
        Args:
            message: The user's input message
            on_assistant_stream: Optional callback for assistant streaming output
            on_tool_stream: Optional callback for tool streaming output
            
        Returns:
            Dictionary containing full response information
        """
        if not self.mcp_ready:
            await self.start_mcp()
        
        response = {
            "assistant_response": "",
            "tool_calls": [],
            "tool_results": []
        }
        
        async with self.agent.iter(message) as run:
            async for node in run:
                if Agent.is_model_request_node(node):
                    async with node.stream(run.ctx) as stream:
                        content = ""
                        if on_assistant_stream:
                            # Use provided callback for streaming
                            content = await on_assistant_stream(stream)
                        else:
                            # Just collect the content without streaming to output
                            async for event in stream:
                                if hasattr(event, 'delta') and hasattr(event.delta, 'content_delta'):
                                    delta = event.delta.content_delta
                                    if delta:
                                        content += delta
                        
                        response["assistant_response"] = content
                        
                elif Agent.is_call_tools_node(node):
                    async with node.stream(run.ctx) as stream:
                        if on_tool_stream:
                            # Use provided callback for tool streaming
                            await on_tool_stream(stream)
                        else:
                            # Collect tool calls and results without streaming
                            async for event in stream:
                                if hasattr(event, 'part') and hasattr(event.part, 'tool_name'):
                                    tool_call = {
                                        "tool_name": event.part.tool_name,
                                        "args": event.part.args
                                    }
                                    response["tool_calls"].append(tool_call)
                                    
                                elif hasattr(event, 'result') and hasattr(event.result, 'content'):
                                    result = event.result.content.content[0].text
                                    response["tool_results"].append(result)
        
        return response