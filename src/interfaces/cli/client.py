import asyncio
import logging
import sys
import os
import json
from utils.logging import log_msg, COLORS
from core.agent import AgentService

# Configure logging to suppress INFO messages from the server
logging.basicConfig(level=logging.WARNING)

class ConversationHistory:
    """Manages conversation history with persistence capabilities."""
    
    def __init__(self, history_file=None):
        self.messages = []
        self.history_file = history_file
        self._load_history()
        
    def _load_history(self):
        """Load conversation history from file if it exists."""
        if not self.history_file or not os.path.exists(self.history_file):
            return
            
        try:
            with open(self.history_file, 'r') as f:
                self.messages = json.load(f)
                log_msg("system", f"Loaded {len(self.messages)} messages from history")
        except Exception as e:
            log_msg("error", f"Failed to load history: {e}")
    
    def save_history(self):
        """Save conversation history to file if configured."""
        if not self.history_file:
            return
            
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.messages, f)
        except Exception as e:
            log_msg("error", f"Failed to save history: {e}")
    
    def add_message(self, role, content):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
    
    def get_recent(self, count=10):
        """Get the most recent messages."""
        if len(self.messages) <= count:
            return self.messages
        return self.messages[-count:]
    
    def clear(self):
        """Clear the conversation history."""
        self.messages = []
        if self.history_file and os.path.exists(self.history_file):
            try:
                os.remove(self.history_file)
            except Exception as e:
                log_msg("error", f"Failed to delete history file: {e}")

async def run_terminal_interface():
    """Run the agent as a terminal interface."""
    log_msg("system", "Pydantic AI Chat Client")
    log_msg("system", "Type 'quit' to exit, 'clear' to clear history.")
    log_msg("system", "Initializing MCP...")
    
    # Create conversation history manager
    history_file = os.path.join(os.path.expanduser("~"), ".pydantic_ai_history.json")
    conversation_history = ConversationHistory(history_file)
    
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
                    
                # Handle special commands
                if user_input.lower() in ["quit", "exit"]:
                    log_msg("system", "Saving history and exiting...")
                    conversation_history.save_history()
                    log_msg("system", "Goodbye!")
                    break
                    
                if user_input.lower() == "clear":
                    conversation_history.clear()
                    log_msg("system", "Conversation history cleared.")
                    continue
                
                # Add user message to history
                conversation_history.add_message("user", user_input)
                
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
                        history=conversation_history.get_recent(),
                        on_assistant_message=on_assistant_message,
                        on_tool_call=on_tool_call,
                        on_tool_result=on_tool_result
                    )
                    
                    # Add assistant response to history
                    assistant_response = "".join(collected_assistant_response)
                    conversation_history.add_message("assistant", assistant_response)
                    
                    # Save history periodically
                    if len(conversation_history.messages) % 5 == 0:
                        conversation_history.save_history()
                    
                except Exception as e:
                    log_msg("error", f"Error processing input: {e}")
                
                print(f"\n{separator}")

    except Exception as e:
        log_msg("error", f"MCP startup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_terminal_interface())