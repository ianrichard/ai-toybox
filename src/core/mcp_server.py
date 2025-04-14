from mcp.server.fastmcp import FastMCP
import datetime
import sys
import time 

print("Starting Dummy MCP Server...", file=sys.stderr)

mcp = FastMCP("DummyToolServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integers."""
    result = a + b
    return result

@mcp.tool()
def get_time() -> str:
    """Gets the current date and time in ISO format."""
    now = datetime.datetime.now().isoformat()
    return now

if __name__ == "__main__":
    mcp.run()