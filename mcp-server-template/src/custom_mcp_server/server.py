import sys
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
import custom_mcp_server.tools
from custom_mcp_server.tools_registry import TOOL_FUNCS, TOOL_DESCRIPTIONS, TOOL_SCHEMAS

logger = logging.getLogger(__name__)


async def serve() -> None:
    logger.info("Starting server.py...")

    server = Server("custom-mcp-server")

    @server.list_tools()
    async def list_tools():
        logger.info("list_tools called")
        return [
            types.Tool(
                name=name,
                description=TOOL_DESCRIPTIONS[name],
                inputSchema=TOOL_SCHEMAS[name],
            )
            for name in TOOL_FUNCS.keys()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        logger.info(f"call_tool called with name={name}, arguments={arguments}")
        if name not in TOOL_FUNCS:
            raise ValueError(f"Unknown tool: {name}")
        try:
            result = TOOL_FUNCS[name](**arguments)
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            logger.error(f"Error in tool '{name}': {e}")
            return [types.TextContent(type="text", text=f"Error: {e}")]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


async def main() -> None:
    await serve()
