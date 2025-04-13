import asyncio
import logging
import sys
from log_utils import log_msg, COLORS
from agent_service import AgentService

# Configure logging to suppress INFO messages from the server
logging.basicConfig(level=logging.WARNING)

async def run_terminal_interface():
    """Run the agent as a terminal interface."""
    log_msg("system", "Pydantic AI Chat Client")
    log_msg("system", "Type 'quit' to exit.")
    log_msg("system", "Initializing MCP...")
    
    # Store conversation history
    conversation_history = []
    
    try:
        async with AgentService() as service:
            log_msg("system", "MCP Ready!")

            while True:
                # Get user input with a clean prompt
                sys.stdout.write(f"{COLORS['green']}user: {COLORS['reset']}")
                sys.stdout.flush()
                user_input = input().strip()
                
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit"]:
                    log_msg("system", "Goodbye!")
                    break
                
                # Add user message to history
                conversation_history.append({"role": "user", "content": user_input})
                
                # Print separator after user input
                separator = "─" * 50
                print(separator)
                sys.stdout.write(f"{COLORS['blue']}assistant: {COLORS['reset']}")
                sys.stdout.flush()
                
                # Define callbacks for terminal output
                collected_assistant_response = []
                
                def on_assistant_message(delta):
                    collected_assistant_response.append(delta)
                    sys.stdout.write(delta)
                    sys.stdout.flush()
                    
                def on_tool_call(tool_call):
                    print(f"\n{separator}")
                    log_msg("tool", f"Calling tool: {tool_call['tool_name']}")
                    print(f"{COLORS['yellow']}{tool_call['args']}{COLORS['reset']}")
                    print(separator)
                    
                def on_tool_result(result):
                    log_msg("tool", "Tool response:")
                    print(f"{COLORS['green']}{result}{COLORS['reset']}")
                    print(separator)
                
                # Process the user input with history context
                try:
                    response = await service.process_input(
                        user_input,
                        history=conversation_history[-10:] if len(conversation_history) > 1 else None,
                        on_assistant_message=on_assistant_message,
                        on_tool_call=on_tool_call,
                        on_tool_result=on_tool_result
                    )
                    
                    # Add assistant response to history
                    conversation_history.append({
                        "role": "assistant", 
                        "content": "".join(collected_assistant_response)
                    })
                    
                except Exception as e:
                    log_msg("error", f"Error processing input: {e}")
                
                print(f"\n{separator}")

    except Exception as e:
        log_msg("error", f"MCP startup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_terminal_interface())