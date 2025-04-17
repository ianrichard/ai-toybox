from mcp.server.fastmcp import FastMCP
from typing import AsyncGenerator
import datetime

mcp = FastMCP("DummyToolServer")

# --- Tools ---

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

@mcp.tool()
def get_time() -> str:
    """Returns the current time in ISO format."""
    return datetime.datetime.now().isoformat()

# --- Resources ---

@mcp.resource("dummy://list-resources")
async def list_resources() -> AsyncGenerator[str, None]:
    """Yields the list of all registered resources."""
    try:
        for uri in mcp._resource_manager._resources.keys():
            yield uri
    except GeneratorExit:
        return
    except Exception as e:
        print(f"⚠️ Error in list_resources: {e}")
        raise

# --- Prompts ---

@mcp.prompt("dummy://echo")
def echo_prompt(input: str) -> dict:
    """Echoes back user input."""
    return {
        "description": "Echoes the input text.",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"You said: {input}"
                }
            }
        ]
    }

# --- Entry point ---

if __name__ == "__main__":
    print("🚀 DummyToolServer running...")
    mcp.run()