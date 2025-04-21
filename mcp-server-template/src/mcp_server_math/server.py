import sys
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from mcp_server_math.tools import math_tools

logger = logging.getLogger(__name__)

async def serve() -> None:
    logger.info("Starting server.py...")

    server = Server("mcp-math")

    # Map tool names to functions
    TOOL_FUNCS = {
        "add": math_tools.add,
        "subtract": math_tools.subtract,
        "multiply": math_tools.multiply,
        "divide": math_tools.divide,
        "dummy_tool": math_tools.dummy_tool,
    }

    TOOL_DESCRIPTIONS = {
        "add": "Add two numbers.",
        "subtract": "Subtract two numbers.",
        "multiply": "Multiply two numbers.",
        "divide": "Divide two numbers (raises error if dividing by zero).",
        "dummy_tool": "A dummy tool that returns a static string for testing.",
    }

    TOOL_SCHEMAS = {
        "add": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
        "subtract": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
        "multiply": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
        "divide": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
        "dummy_tool": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    @server.list_tools()
    async def list_tools():
        logger.info("list_tools called")
        return [
            types.Tool(
                name=name,
                description=TOOL_DESCRIPTIONS[name],
                inputSchema=TOOL_SCHEMAS[name],
            ) for name in TOOL_FUNCS.keys()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        logger.info(f"call_tool called with name={name}, arguments={arguments}")
        if name not in TOOL_FUNCS:
            raise ValueError(f"Unknown tool: {name}")
        try:
            # For dummy_tool (no args)
            if name == "dummy_tool":
                result = TOOL_FUNCS[name]()
            else:
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
