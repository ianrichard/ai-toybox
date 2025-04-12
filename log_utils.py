import asyncio
import logging
from typing import AsyncGenerator, Any, Optional

# Configure logging to suppress INFO messages from the server
logging.basicConfig(level=logging.WARNING)

def log_msg(role: str, msg: str):
    """
    Simple function to log messages with appropriate prefixes based on role.
    
    Args:
        role: The source of the message ('user', 'assistant', 'tool', 'system', 'error')
        msg: The message content
    """
    separator = "─" * 50  # Use a consistent separator character and length
    
    match role:
        case "system":
            print(f"system: {msg}")
        case "error":
            print(f"error: {msg}")
        case "user":
            print(separator)
            print(f"user:")
            print(f"{msg}")
            print(separator)
        case "assistant":
            print(f"assistant:")
            print(f"{msg}")
            print(separator)
        case "tool":
            # Tool messages are handled differently
            pass
        case _:
            print(msg)


async def log_stream(role: str, stream: AsyncGenerator) -> str:
    """
    Process and log a stream of events with appropriate formatting.
    Returns the collected content for further use.
    
    Args:
        role: The source of the stream ('assistant', 'tool', etc)
        stream: AsyncGenerator producing events to be processed and logged
        
    Returns:
        The collected content as a string (for assistant streams)
    """
    # Track whether we've seen any content
    collected_content = ""
    tool_calls = []
    tool_results = []
    separator = "─" * 50  # Use a consistent separator character and length
    
    if role == "assistant":
        print(separator)
        print("assistant:")
    
    async for event in stream:
        # Process different event types based on their structure
        if hasattr(event, 'delta') and hasattr(event.delta, 'content_delta'):
            # Model response text deltas
            delta = event.delta.content_delta
            if delta:
                print(delta, end="", flush=True)
                collected_content += delta
                
        elif hasattr(event, 'part') and hasattr(event.part, 'tool_name'):
            # Tool call events - only print if there are arguments
            if event.part.args and event.part.args.strip() not in ["", "{}"]:
                tool_call = {
                    "tool_name": event.part.tool_name,
                    "args": event.part.args
                }
                tool_calls.append(tool_call)
                print(separator)
                print(f"tool call:")
                print(f"{event.part.args}")
                print(separator)
            
        elif hasattr(event, 'result') and hasattr(event.result, 'content'):
            # Tool result events
            result = event.result.content.content[0].text
            tool_results.append(result)
            print("tool response:")
            print(f"{result}")
            print(separator)
    
    # Print a newline before the closing separator for assistant responses
    if role == "assistant" and collected_content:
        print("\n" + separator)  # Add a newline before the separator
        
    # For assistant streams, return the collected content
    if role == "assistant":
        return collected_content
    
    # For tool streams, return structured data
    if role == "tool":
        return {"tool_calls": tool_calls, "tool_results": tool_results}
    
    return ""