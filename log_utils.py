def log_msg(role: str, msg: str):
    """
    Simple function to log messages with appropriate prefixes based on role.
    
    Args:
        role: The source of the message ('user', 'assistant', 'tool', 'system', 'error')
        msg: The message content
    """
    match role:
        case "user":
            print(f"user: {msg}")
        case "assistant":
            print(f"assistant: {msg}")
        case "tool":
            print(f"tool: {msg}")
        case "system":
            print(f"system: {msg}")
        case "error":
            print(f"error: {msg}")
        case _:
            print(msg)