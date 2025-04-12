import asyncio
import sys
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.messages import (
    PartDeltaEvent,
    TextPartDelta,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
)
from log_utils import log_msg

agent = Agent(
    "openai:gpt-4o-mini",
    mcp_servers=[MCPServerStdio(sys.executable, args=["mcp_dummy_server.py"])],
    system_prompt=(
        "You are a helpful assistant."
    ),
)


async def run_chat():
    log_msg("system", "Pydantic AI Chat Client")
    log_msg("system", "Type 'quit' to exit.")
    log_msg("system", "Initializing MCP...")

    try:
        async with agent.run_mcp_servers():
            log_msg("system", "MCP Ready!\n")

            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() == "quit":
                        break
                    if not user_input:
                        continue

                    async with agent.iter(user_input) as run:
                        async for node in run:
                            if Agent.is_model_request_node(node):
                                async with node.stream(run.ctx) as stream:
                                    async for event in stream:
                                        if isinstance(
                                            event, PartDeltaEvent
                                        ) and isinstance(event.delta, TextPartDelta):
                                            delta = event.delta.content_delta
                                            print(delta, end="")
                                print()

                            elif Agent.is_call_tools_node(node):
                                async with node.stream(run.ctx) as stream:
                                    async for event in stream:
                                        if isinstance(event, FunctionToolCallEvent):
                                            log_msg(
                                                "tool",
                                                f"Calling {event.part.tool_name} with {event.part.args}",
                                            )
                                        elif isinstance(event, FunctionToolResultEvent):
                                            log_msg("tool", event.result.content.content[0].text)
                except Exception as e:
                    log_msg("error", str(e))

    except Exception as e:
        log_msg("error", f"MCP startup failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_chat())
