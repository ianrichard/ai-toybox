# MCP LLM API Server

An API server for LLMs using the Model-Call-Protocol pattern and Pydantic AI.

## Features

| Feature                                  | Benefit (Plain English)                             | Current State                         | Future State                                                          |
| ---------------------------------------- | --------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------- |
| Chat Web UI                              | Simple chat interface, easy to use                  | Basic React UI, minimal styling       | More robust, polished UI, possibly with reusable web components       |
| Streaming responses                      | See answers as they come in—faster feedback         | Implemented                           | May be improved for responsiveness and more formats                   |
| Custom MCP server with placeholder tools | Extensible backend, can add your own tools          | Has sample tools, minimally organized | Dedicated examples/templates in their own directory and setup helpers |
| Tool calls through MCP                   | Integrate outside resources (APIs, code, data)      | Static tools                          | Dynamic tool loading, prompt and resource management                  |
| MCP inspector                            | Debug and inspect what’s happening “under the hood” | Functional, but occasionally unstable | Improved stability, works reliably with aggregate servers             |
| MCP config JSON                          | Easily tweak system settings in one file            | Supports basic use cases              | Thoroughly tested, supports more advanced configs                     |
| Any model provider via PydanticAI        | Use any AI model you want, seamlessly swap models   | Supported, just swap configs          | Ongoing, with community models and docs                               |
| Docker integration                       | Fast setup, “works on my machine” everywhere        | MVP version, may have bugs            | Refined, stable, easier for all environments                          |

## Prerequisites

- Docker

## Quick Start

1. **Clone the repo**
   ```bash
   git clone https://github.com/ianrichard/mcp-llm-api-server.git
   cd mcp-llm-api-server
   ```
2. **Copy example environment file**
   ```bash
   cp .env.example .env
   ```
3. **Change .env to your provider and model**

- You only need the API key for the provider.
- This project follows [PydanticAI's provider:model syntax](https://ai.pydantic.dev/models/).
- [Groq](https://groq.com/) is a quick and simple solution to try things out. (No affiliation, just think it's good)

4. **Start the API server:**
   ```bash
   docker-compose up --build
   ```
5. The API server will be available at [http://localhost:8000](http://localhost:8000).

### Azure OpenAI Configuration

To use Azure OpenAI as a provider, fill out the additional fields provided in the example `.env.example`

## API Documentation

The chat web server API is available through the Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs).

## Web Client

A demo web client is included in the `/chat` directory and is served at:

    http://localhost:8000/

It uses web sockets and streaming.

## MCP Inspector

You can open [http://localhost:6274/](http://localhost:6274/) in your browser to inspect and interact with the MCP server.

- The inspector connects to your Python MCP server running in the same Docker environment.
- Useful for debugging, testing, and visualizing MCP tool calls and responses.

### 1. Standalone MCP Server

A standalone MCP server exposes only its own tools/resources.

```bash
python src/mcp/mcp_server.py
```

### 2. Aggregate MCP Server

An aggregate MCP server combines multiple MCP servers (local or subprocesses) under one endpoint, namespaced by prefix.
Configuration is managed in [mcp_config.json](./mcp_config.json), following [the Anthropic convention](https://modelcontextprotocol.io/quickstart/user#mac-os-linux).

```bash
python src/mcp/mcp_aggregate_server.py
```

The base [agent.py](./src/chat/agent.py) runs a script that uses this aggregate for its tooling.

There are currently issues running the aggregate server in the web UI and the app at the same time. The FastMCP API is relatively new and exception handling around missing tools is not quite there, so for now just using `mcp_server.py` is good enough due to the fact that that's what you'd be working on anyway vs testing industry libraries.
