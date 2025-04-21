from .registry import tool

@tool
def dummy_tool() -> str:
    """A dummy tool that returns a static string for testing purposes."""
    return "This is a dummy tool response."