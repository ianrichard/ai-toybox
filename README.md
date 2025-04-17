# MCP LLM API Server

An API server for LLMs using the Model-Call-Protocol pattern and Pydantic AI.

## Features

- API server with WebSocket streaming
- Web client demonstration
- Tool call support through MCP

## Prerequisites

- Docker and Docker Compose

## Quick Start

1. Copy `.env.example` to `.env` and add your API keys.

2. **Start the API server:**
   ```bash
   docker-compose up --build
   ```

3. The API server will be available at [http://localhost:8000](http://localhost:8000).

## Model Configuration

Set the `BASE_MODEL` and API keys in your `.env` file:

```env
BASE_MODEL=groq:llama-3.3-70b-versatile
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## API Documentation

Once running, access:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Making API Calls

Example using curl:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello, agent!"}' http://localhost:8000/chat
```

WebSocket endpoint:
```
ws://localhost:8000/ws
```

## Web Client

A demo web client is included in the `/static` directory. Access it at:

```
http://localhost:8000/
```

---

*The API server runs on port 8000 by default.*

## MCP Inspector

The MCP Inspector is available for development and debugging at:

**http://localhost:6274/**

After running:

```sh
docker-compose up --build
```

You can open [http://localhost:6274/](http://localhost:6274/) in your browser to inspect and interact with the MCP server.

- The inspector connects to your Python MCP server running in the same Docker environment.
- Useful for debugging, testing, and visualizing MCP tool calls and responses.

---

## MCP Server Modes: Standalone vs Aggregate

You can run this project in two ways:

### 1. Standalone MCP Server

A standalone MCP server exposes only its own tools/resources.  
Example: `src/mcp/mcp_server.py`

**Run it directly:**
```bash
python src/mcp/mcp_server.py
```
or
```bash
fastmcp run src/mcp/mcp_server.py
```

---

### 2. Aggregate MCP Server

An aggregate MCP server combines multiple MCP servers (local or subprocesses) under one endpoint, namespaced by prefix.  
Configuration is managed in `mcp_config.json`.

**Example `mcp_config.json`:**
```json
{
  "servers": [
    {
      "name": "local",
      "transport": {
        "command": "python",
        "args": ["src/mcp/mcp_server.py"],
        "env": {}
      }
    },
    {
      "name": "filesystem",
      "transport": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"],
        "env": {}
      }
    }
  ]
}
```

**Run the aggregate server:**
```bash
python src/mcp/mcp_aggregate_server.py mcp_config.json
```
or
```bash
fastmcp run src/mcp/mcp_aggregate_server.py mcp_config.json
```

---

**When to use which?**

- Use **standalone** for simple, single-tool servers or development.
- Use **aggregate** to combine multiple MCP servers (local and/or subprocesses) into a single endpoint for production or unified toolsets.

You can add or remove subprocess servers by editing `mcp_config.json`—no code changes needed!