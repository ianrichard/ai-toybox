# MCP Server Template (Python)

A template for building Model Context Protocol (MCP) servers in Python. This example implements basic math operations as tools for LLMs and MCP clients.

## Overview

This template demonstrates how to structure and implement an MCP server in Python. The example exposes simple math tools (add, subtract, multiply, divide) via MCP, similar to other sibling servers (e.g., time, sqlite).

## Usage

### Local Development (Recommended for Fast Iteration)

1. **Install [uv](https://github.com/astral-sh/uv) and create a virtual environment:**

   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install --editable .
   ```

2. **Run the server with MCP Inspector:**

   ```bash
   npx @modelcontextprotocol/inspector python -m mcp_server_math --verbose
   ```

   - This will launch the server using your local code, with live code reload (edit and rerun, no rebuild needed)
   - Open http://127.0.0.1:6274 to interact with the server in the Inspector UI
   - The Inspector will use STDIO as the transport type with `python` as the command

### Run from Docker Build

This scenario is for running your MCP server as a standalone, production-like container.
When you build the image, it is registered in your local Docker image registry under the name you specify (here, `mcp-server-math`).
You can then run this image from any project or terminal on your machine.

1. **Build the Docker image:**

   ```bash
   docker build -t mcp-server-math .
   ```

   - This command packages your code and its dependencies into a Docker image named `mcp-server-math`.
   - The image is stored locally and can be referenced by name.

2. **Run the server with MCP Inspector via Docker:**

   ```bash
   npx @modelcontextprotocol/inspector docker run -i --rm mcp-server-math
   ```

   - This starts the server in a container and connects it to the Inspector UI
   - The Inspector will use STDIO with `docker` as the command
   - You can run this image from any directory or project on your machine, as long as the image exists locally.

## Docker Development

- Start the dev container:

  ```bash
  docker compose up --build
  ```

- In another terminal, connect Inspector to the running container:

  ```bash
  npx @modelcontextprotocol/inspector docker exec -i <container_name> python -m mcp_server_math --verbose
  ```

  (Replace <container_name> with your actual container name.)

**Note:**
Hot reloading in Docker dev mode may have connection issues or require server restarts for changes to take effect.
For the smoothest development experience, running the server directly with Python on your host is recommended:

    ```bash
    npx @modelcontextprotocol/inspector python -m mcp_server_math --verbose
    ```

## Tool System

The server provides math operation tools via the Model Context Protocol. These tools are implemented in the tools package and registered with the server.

Tools are organized in their own directory to:

- Maintain separation of concerns
- Allow easy addition of new tool categories
- Enable modular testing and development

Each tool is a Python function with type annotations that gets exposed through the MCP interface, with automatically generated schema information for parameters and return values.

### Known Issues

- **Inspector + Windsurf**: When running the Inspector with Windsurf running, the Inspector process may keep re-spawning and fail to maintain a connection. Stop Windsurf before using the Inspector.
- STDIO communication relies on specific formatting; ensure proper serialization/deserialization.

## License

MIT
