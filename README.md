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

2. **Build the Docker image:**
   ```bash
   docker-compose build
   ```

3. **Start the API server:**
   ```bash
   docker-compose up
   ```

4. The API server will be available at [http://localhost:8000](http://localhost:8000).

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