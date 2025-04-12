import asyncio
import sys
import logging
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from log_utils import log_msg, log_stream

# Configure logging to suppress INFO messages from the server
logging.basicConfig(level=logging.WARNING)

async def run_terminal_interface():
    """Run the agent as a terminal interface."""
    agent = Agent(
        "openai:gpt-4o-mini",
        mcp_servers=[MCPServerStdio(sys.executable, args=["mcp_server.py"])],
        system_prompt=(
            "You are a helpful assistant."
        ),
    )
    
    log_msg("system", "Pydantic AI Chat Client")
    log_msg("system", "Type 'quit' to exit.")
    log_msg("system", "Initializing MCP...")

    try:
        async with agent.run_mcp_servers():
            log_msg("system", "MCP Ready!\n")

            while True:
                # Get user input with a clean "user: " prompt
                user_input = input("user: ").strip()
                
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    break
                
                # No need to log the user message since the input prompt already shows it
                separator = "─" * 50
                print(separator)

                try:
                    async with agent.iter(user_input) as run:
                        async for node in run:
                            if Agent.is_model_request_node(node):
                                async with node.stream(run.ctx) as stream:
                                    await log_stream("assistant", stream)
                                    
                            elif Agent.is_call_tools_node(node):
                                async with node.stream(run.ctx) as stream:
                                    await log_stream("tool", stream)
                                    
                except Exception as e:
                    log_msg("error", str(e))

    except Exception as e:
        log_msg("error", f"MCP startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_terminal_interface())