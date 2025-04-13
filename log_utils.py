"""Utility functions for terminal logging with colors."""
import sys
from datetime import datetime

# ANSI color codes for terminal output
COLORS = {
    "reset": "\033[0m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
}

def log_msg(msg_type, message):
    """Print a formatted log message with timestamp and color based on type.
    
    Args:
        msg_type: Type of message (system, user, assistant, error, tool)
        message: The message content to display
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Color mapping for different message types
    color_map = {
        "system": COLORS["cyan"],
        "user": COLORS["green"],
        "assistant": COLORS["blue"],
        "error": COLORS["red"],
        "tool": COLORS["yellow"],
    }
    
    # Default to white if type not in map
    color = color_map.get(msg_type.lower(), COLORS["white"])
    
    # Format and print the message
    prefix = f"[{timestamp}] {msg_type.upper()}: "
    print(f"{color}{prefix}{message}{COLORS['reset']}")