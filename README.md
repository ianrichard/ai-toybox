# MCP LLM API Server

An API server for LLMs using the Model-Call-Protocol pattern and Pydantic AI.

## Features

- Terminal interface for CLI interaction
- API server with WebSocket streaming
- Web client demonstration
- Tool call support through MCP

## Prerequisites

- Python 3.9+
- A virtual environment (venv)

## Quick Start (Local Development)

1. Copy `.env.example` to `.env` and add your API keys
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the CLI:
   ```bash
   python src/main.py --mode cli
   ```
5. Run the API:
   ```bash
   python src/main.py --mode api
   ```

## Docker

### Build the Docker image
```bash
docker build -t mcp-llm-api-server .
```

### Running API mode (default)
```bash
docker run -p 8000:8000 --env-file .env mcp-llm-api-server
```

### Running CLI mode (interactive)
```bash
docker run -it --env-file .env mcp-llm-api-server --mode cli
```

### Docker Development with Live Reloading
```bash
# Run with volume mount for live code reloading during development
docker run -p 8000:8000 --env-file .env -v $(pwd):/app mcp-llm-api-server
```

### Using Docker Compose
```bash
# Start the API service
docker-compose up
```

## Model Configuration

This project uses [Pydantic AI](https://ai.pydantic.dev/) for AI model integration. You can configure which model to use by setting the `BASE_MODEL` environment variable.

The format follows the Pydantic AI convention: `provider:model_name`

Examples:
- `openai:gpt-4o`
- `anthropic:claude-3-opus-20240229`
- `groq:llama-3.3-70b-versatile`

See the complete list of supported models at: [https://ai.pydantic.dev/models/](https://ai.pydantic.dev/models/)

### API Keys

For each provider, you'll need to set the corresponding API key in your `.env` file:

```bash
# Example .env configuration
BASE_MODEL=groq:llama-3.3-70b-versatile
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

The API key environment variable follows the pattern: `{PROVIDER_NAME}_API_KEY`

## API Documentation

Once the API server is running, access the auto-generated API documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Making API Calls

The primary endpoint is `/chat`, which accepts POST requests with a JSON body containing the user's message.

Example using curl:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello, agent!"}' http://localhost:8000/chat
```

For streaming responses, use the WebSocket endpoint:
```
ws://localhost:8000/ws
```

## Web Client

A demo web client is included in the `/static` directory. Access it at:

```
http://localhost:8000/
```

## Important Notes

* Ensure that the virtual environment is activated before running either the client or the server.
* The API server runs on port 8000 by default.
* Both the CLI interface and API server use the same underlying agent functionality.