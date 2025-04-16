from mcp.server.fastmcp import FastMCP
import datetime

mcp = FastMCP("DummyToolServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integers."""
    return a + b

@mcp.tool()
def get_time() -> str:
    """Gets the current date and time in ISO format."""
    return datetime.datetime.now().isoformat()

if __name__ == "__main__":
    mcp.run()