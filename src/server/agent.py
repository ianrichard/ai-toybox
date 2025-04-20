import asyncio
import atexit
import json
import logging
import os
import signal

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.azure import AzureProvider

from src.server.utils.mcp_config import load_mcp_config
from src.server.utils.logging import setup_logging

setup_logging()
logger = logging.getLogger("core.agent")


load_dotenv()

MCP_CONFIG = load_mcp_config()

class AgentService:
    def __init__(self, system_prompt: str = "You are a helpful assistant. Only use tools if needed for a user query."):
        model_name = os.getenv("BASE_MODEL")
        if not model_name:
            logger.error("BASE_MODEL environment variable is not set")
            raise ValueError("BASE_MODEL environment variable is required")
        self.mcp_servers = []
        for server_conf in MCP_CONFIG:
            transport = server_conf.get("transport", {})
            command = transport.get("command")
            args = transport.get("args", [])
            env = transport.get("env", {})
            if not command:
                continue
            server = MCPServerStdio(
                command,
                args=args,
                env=env,
            )
            self.mcp_servers.append(server)
        if model_name.startswith("azure:"):
            base = model_name.split(":", 1)[1]
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
            azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not all([azure_endpoint, azure_api_version, azure_api_key]):
                logger.error("Azure OpenAI config missing in environment variables")
                raise RuntimeError("Azure OpenAI config missing in environment variables")
            model = OpenAIModel(
                base,
                provider=AzureProvider(
                    azure_endpoint=azure_endpoint,
                    api_version=azure_api_version,
                    api_key=azure_api_key,
                ),
            )
            self.agent = Agent(
                model,
                mcp_servers=self.mcp_servers,
                system_prompt=system_prompt,
            )
        else:
            self.agent = Agent(
                model_name,
                mcp_servers=self.mcp_servers,
                system_prompt=system_prompt,
            )
        self._cleanup_registered = False

    async def __aenter__(self):
        self._mcp_context = self.agent.run_mcp_servers()
        await self._mcp_context.__aenter__()
        self._register_cleanup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._mcp_context.__aexit__(exc_type, exc_val, exc_tb)

    async def process_input(
        self,
        user_input,
        history=None,
        on_assistant_message=None,
        on_tool_call=None,
        on_tool_result=None,
    ):
        response = {"assistant_content": "", "tool_calls": [], "tool_results": []}
        try:
            input_with_context = (
                user_input
                if not history
                else f"Previous conversation:\n{json.dumps(history, indent=2)}\n\nCurrent query: {user_input}"
            )
            async with self.agent.iter(input_with_context) as run:
                async for node in run:
                    if self.agent.is_model_request_node(node):
                        await self._handle_model_request(
                            node, run.ctx, response, on_assistant_message
                        )
                    elif self.agent.is_call_tools_node(node):
                        await self._handle_tool_call(
                            node, run.ctx, response, on_tool_call, on_tool_result
                        )
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            response["error"] = str(e)
        return response

    async def _handle_model_request(self, node, ctx, response, on_assistant_message):
        async with node.stream(ctx) as stream:
            content = ""
            async for event in stream:
                if hasattr(event, "delta") and hasattr(event.delta, "content_delta"):
                    delta = event.delta.content_delta
                    if delta:
                        content += delta
                        if on_assistant_message:
                            on_assistant_message(delta)
            response["assistant_content"] = content

    async def _handle_tool_call(
        self, node, ctx, response, on_tool_call, on_tool_result
    ):
        async with node.stream(ctx) as stream:
            async for event in stream:
                tool_data = {"type": "tool"}
                if hasattr(event, "part") and hasattr(event.part, "tool_name"):
                    tool_data["id"] = (
                        event.call_id
                        if hasattr(event, "call_id")
                        else event.tool_call_id
                    )
                    tool_data["name"] = event.part.tool_name
                    if event.part.args and event.part.args.strip() not in ["", "{}"]:
                        tool_data["args"] = event.part.args
                    response["tool_calls"].append(tool_data.copy())
                    if on_tool_call:
                        on_tool_call(tool_data)
                elif hasattr(event, "result") and hasattr(event.result, "content"):
                    result_text = event.result.content.content[0].text
                    tool_data["name"] = getattr(event.result, "tool_name", "unknown")
                    tool_data["id"] = (
                        event.tool_call_id
                        if hasattr(event, "tool_call_id")
                        else "unknown_tool"
                    )
                    tool_data["results"] = result_text
                    response["tool_results"].append(tool_data.copy())
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