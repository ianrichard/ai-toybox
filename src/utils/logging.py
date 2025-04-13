"""Utility functions for terminal logging with colors."""
import sys
import os
from datetime import datetime

# Check if colors should be enabled
def _supports_color():
    """Determine if the current environment supports color output."""
    # Check for NO_COLOR environment variable (standard way to disable colors)
    if 'NO_COLOR' in os.environ:
        return False
        
    # Check for FORCE_COLOR environment variable
    if 'FORCE_COLOR' in os.environ:
        return True
        
    # Check if output is redirected
    if not sys.stdout.isatty():
        return False
        
    # Platform-specific checks
    plat = sys.platform
    if plat == 'win32':
        # On Windows, check for ANSICON, ConEmu, Windows Terminal, or WSL
        return (
            'ANSICON' in os.environ
            or 'WT_SESSION' in os.environ
            or 'ConEmuANSI' in os.environ
            or os.environ.get('TERM_PROGRAM') == 'vscode'
            or 'WSL_DISTRO_NAME' in os.environ
        )
        
    return True

# Enable Windows ANSI support if needed
if sys.platform == 'win32' and _supports_color():
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

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

# Disable colors if not supported
USE_COLORS = _supports_color()
if not USE_COLORS:
    COLORS = {k: "" for k in COLORS}  # Empty strings if colors not supported

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