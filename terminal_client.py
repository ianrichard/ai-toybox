import asyncio
import logging
from log_utils import log_msg
from agent_service import AgentService

# Configure logging to suppress INFO messages from the server
logging.basicConfig(level=logging.WARNING)

async def run_terminal_interface():
    """Run the agent as a terminal interface."""
    log_msg("system", "Pydantic AI Chat Client")
    log_msg("system", "Type 'quit' to exit.")
    log_msg("system", "Initializing MCP...")
    
    try:
        async with AgentService() as service:
            log_msg("system", "MCP Ready!\n")

            while True:
                # Get user input with a clean "user: " prompt
                user_input = input("user: ").strip()
                
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    break
                
                # Print separator after user input
                separator = "─" * 50
                print(separator)
                print("assistant:")
                
                # Define callbacks for terminal output
                def on_assistant_message(delta):
                    print(delta, end="", flush=True)
                    
                def on_tool_call(tool_call):
                    print(f"\n{separator}")
                    print(f"tool call:")
                    print(f"{tool_call['args']}")
                    print(separator)
                    
                def on_tool_result(result):
                    print("tool response:")
                    print(f"{result}")
                    print(separator)
                
                # Process the user input
                await service.process_input(
                    user_input,
                    on_assistant_message=on_assistant_message,
                    on_tool_call=on_tool_call,
                    on_tool_result=on_tool_result
                )
                print(f"\n{separator}")

    except Exception as e:
        log_msg("error", f"MCP startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_terminal_interface())