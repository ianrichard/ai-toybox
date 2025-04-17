import asyncio
import sys
import os
import json
import logging
import signal
import atexit
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from typing import AsyncGenerator, Optional, Dict, Any, Callable, Union

# Set up proper logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("core.agent")

load_dotenv()  # Load environment variables from .env


class AgentService:
    """Core service layer for agent interactions that can be used by multiple frontends."""

    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant. Only use tools if needed for a user query.",
    ):
        model_name = os.getenv("BASE_MODEL")
        if not model_name:
            logger.error("BASE_MODEL environment variable is not set")
            raise ValueError("BASE_MODEL environment variable is required")

        logger.info(f"Initializing agent with model: {model_name}")

        # Define list of MCP servers
        mcp_servers = [
            # Always include the Python MCP server
            MCPServerStdio(sys.executable, args=["src/mcp/mcp_aggregate_server.py"])
        ]

        # mcp_servers.append(
        #     MCPServerStdio(
        #         "python",
        #         args=[
        #             "-m",
        #             "mcp_server_fetch"
        #         ],
        #     )
        # )

        # Initialize the agent with the available MCP servers
        self.agent = Agent(
            model_name,
            mcp_servers=mcp_servers,
            system_prompt=system_prompt,
        )
        self._cleanup_registered = False

    async def __aenter__(self):
        """Start MCP servers when used as context manager."""
        self._mcp_context = self.agent.run_mcp_servers()
        await self._mcp_context.__aenter__()
        self._register_cleanup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop MCP servers when exiting context."""
        await self._mcp_context.__aexit__(exc_type, exc_val, exc_tb)

    async def process_input(
        self,
        user_input: str,
        history: Optional[list] = None,
        on_assistant_message: Optional[Callable] = None,
        on_tool_call: Optional[Callable] = None,
        on_tool_result: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Process user input and handle the agent response.

        Args:
            user_input: The text input from the user
            history: Optional conversation history
            on_assistant_message: Callback for streaming assistant responses
            on_tool_call: Callback for tool calls
            on_tool_result: Callback for tool results

        Returns:
            Dict containing assistant response, tool calls and results
        """
        response = {"assistant_content": "", "tool_calls": [], "tool_results": []}

        try:
            # Format history in a cleaner way if provided
            input_with_context = self._prepare_input_with_history(user_input, history)
            logger.info(f"Processing input: {user_input[:50]}...")

            async with self.agent.iter(input_with_context) as run:
                await self._process_agent_run(
                    run, response, on_assistant_message, on_tool_call, on_tool_result
                )

        except Exception as e:
            logger.exception(f"Error processing input: {e}")
            response["error"] = str(e)

        return response

    def _prepare_input_with_history(
        self, user_input: str, history: Optional[list]
    ) -> str:
        """Prepare the input with context from conversation history if available."""
        if not history:
            return user_input

        return f"Previous conversation:\n{json.dumps(history, indent=2)}\n\nCurrent query: {user_input}"

    async def _process_agent_run(
        self,
        run,
        response: Dict[str, Any],
        on_assistant_message: Optional[Callable],
        on_tool_call: Optional[Callable],
        on_tool_result: Optional[Callable],
    ):
        """Process the agent run and update the response dictionary."""
        async for node in run:
            if self.agent.is_model_request_node(node):
                await self._handle_model_request(
                    node, run.ctx, response, on_assistant_message
                )

            elif self.agent.is_call_tools_node(node):
                await self._handle_tool_call(
                    node, run.ctx, response, on_tool_call, on_tool_result
                )

    async def _handle_model_request(self, node, ctx, response, on_assistant_message):
        """Process model generation events."""
        async with node.stream(ctx) as stream:
            collected_content = ""
            async for event in stream:
                logger.debug(f"Model event: {type(event)}")
                if hasattr(event, "delta") and hasattr(event.delta, "content_delta"):
                    delta = event.delta.content_delta
                    if delta:
                        collected_content += delta
                        if on_assistant_message:
                            on_assistant_message(delta)

            response["assistant_content"] = collected_content

    async def _handle_tool_call(
        self, node, ctx, response, on_tool_call, on_tool_result
    ):
        """Process tool call events."""
        async with node.stream(ctx) as stream:
            async for event in stream:
                logger.error(f"----------------")
                logger.error(f"{event}")
                logger.error(f"----------------")

                # Initialize common tool data structure
                tool_data = {"type": "tool"}

                # Handle tool call
                if hasattr(event, "part") and hasattr(event.part, "tool_name"):
                    # Extract tool call ID and name
                    tool_data["id"] = (
                        event.call_id
                        if hasattr(event, "call_id")
                        else event.tool_call_id
                    )
                    tool_data["name"] = event.part.tool_name

                    if event.part.args and event.part.args.strip() not in ["", "{}"]:
                        # Add arguments to the tool data
                        tool_data["args"] = event.part.args

                        # Add to response structure for returning later
                        response["tool_calls"].append(tool_data.copy())

                        # Call the callback if provided
                        if on_tool_call:
                            on_tool_call(tool_data)

                # Handle tool result
                elif hasattr(event, "result") and hasattr(event.result, "content"):
                    # Extract the result text
                    result_text = event.result.content.content[0].text

                    # Get tool name if available
                    if hasattr(event.result, "tool_name"):
                        tool_data["name"] = event.result.tool_name
                    else:
                        tool_data["name"] = "unknown"

                    # Get tool ID if available
                    tool_data["id"] = (
                        event.tool_call_id
                        if hasattr(event, "tool_call_id")
                        else "unknown_tool"
                    )

                    # Add results to the tool data
                    tool_data["results"] = result_text

                    # Add to response structure for returning later
                    response["tool_results"].append(tool_data.copy())

                    # Call the callback if provided
                    if on_tool_result:
                        on_tool_result(tool_data)

    def _register_cleanup(self):
        if self._cleanup_registered:
            return

        def sync_cleanup():
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._mcp_context.__aexit__(None, None, None))
                else:
                    loop.run_until_complete(
                        self._mcp_context.__aexit__(None, None, None)
                    )
            except Exception as e:
                logger.error(f"Error during MCP cleanup: {e}")

        atexit.register(sync_cleanup)
        signal.signal(signal.SIGTERM, lambda *args: sync_cleanup())
        signal.signal(signal.SIGINT, lambda *args: sync_cleanup())
        self._cleanup_registered = True
