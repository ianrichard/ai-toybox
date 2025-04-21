# AI Agent Starter with PydanticAI and MCP

A base project using PydanticAI’s Agent API. Connects to any LLM provider (such as OpenAI, Groq, Azure OpenAI, etc.) and supports multiple MCP servers using a simple JSON config at the root of the project. Includes a minimal demo client to show tool calls and results.

## Features

- **Multi-provider support:** Use any LLM provider with PydanticAI via `provider:model` syntax
  (e.g. `openai:gpt-4o`, `groq:llama-3.3-70b-versatile`)
- **Multiple MCP servers:** Connect to several MCP servers, configured via `mcp_config.json`
  (modeled after the [Claude Desktop convention](https://modelcontextprotocol.io/quickstart/user))
- **Demo client included:** See basic tool call and agent response handling in action

## Prerequisites

- [Docker](https://www.docker.com/)
- [UV](https://github.com/astral-sh/uv) (alternative)

## Quickstart

1. **Clone the repo:**
   ```bash
   git clone https://github.com/ianrichard/mcp-llm-api-server.git
   cd mcp-llm-api-server
   ```
1. **Copy example environment file**
   `cp .env.example .env`
1. **Edit `.env` with your provider and API key(s)**
   - Only the provider API key is needed for most providers.
   - See `.env.example` for the required fields for each provider.
   - This project uses [PydanticAI's provider:model syntax](https://ai.pydantic.dev/models/).
   - [Groq](https://groq.com/) is a simple provider to start with (no affiliation).
1. **[Optional] Set up multiple MCP servers**
   - Add/edit entries in `mcp_config.json` at the root.
     Follow the structure in the [MCP protocol quickstart](https://modelcontextprotocol.io/quickstart/user).
1. **Start the API server with Docker:**
   `docker-compose up --build`

Once running, visit [http://localhost:8000](http://localhost:8000/) in your browser.

### Running with UV

1. Install uv
   `pip install --upgrade uv`
1. Install dependencies
   `uv sync`
1. Start the server
   `uv run -- uvicorn src.server.server:app --host 0.0.0.0 --port 8000`

---

### Azure OpenAI Configuration

To use Azure OpenAI instead of regular OpenAI:

- Fill out the additional Azure fields in your `.env` (see `.env.example`).
- Make sure to specify your Azure endpoint, API key, and deployment/model names as described in the [PydanticAI docs](https://ai.pydantic.dev/models/).

---

## Using 3rd-Party or Custom MCP Servers

If you want to test 3rd-party or custom MCP servers, you can use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).
Simply run it like this in your terminal:

`npx @modelcontextprotocol/inspector -- uvx mcp-server-fetch`

**How it works:**

- The text after the `--` (for example, `uvx mcp-server-fetch`) is _not_ part of the Inspector, but is the actual code or server command passed to it.
- That code is what gets executed when you hit "Connect" in the Inspector UI.
- You can use any server module or command—just change what's after the `--`.

**Pay attention to your environment:**

- Whatever you put after `--` is executed in the shell where you ran `npx @modelcontextprotocol/inspector`.
- That means the required runtime (node, python, etc.) and any dependencies must be available there.
- If you reference a custom or 3rd-party server in your `mcp_config.json`, make sure your local machine or Docker container (depending on where you run this project) has all the interpreters, runtimes, and environment set up appropriately.
