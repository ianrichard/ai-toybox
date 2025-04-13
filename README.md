# Pydantic AI MCP

An AI assistant built with Pydantic AI and the Model-Call-Protocol pattern.

## Features

- Terminal interface for CLI interaction
- API server with WebSocket streaming
- Web client demonstration
- Tool call support through MCP

## Quick Start

1. Copy `.env.example` to `.env` and add your API keys
2. Install dependencies: `pip install -e .`
3. Run the CLI: `python main.py --mode cli`
4. Run the API: `python main.py --mode api`

## Docker

```bash
docker-compose up
```

## Prerequisites

- Python 3.9+
- A virtual environment (venv)

## Installation

1.  **Create and activate a virtual environment:**
```
bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    # or
    .venv\Scripts\activate  # On Windows
    
```
2.  **Install dependencies:**
```
bash
    pip install -r requirements.txt
    
```
## Running the Terminal Client

The `terminal_client.py` file provides a command-line interface for interacting with the agent service.  To run the client, execute the following command from the project's root directory:
```
bash
python terminal_client.py
```
This will start the terminal client, and you can then interact with the agent by typing messages and pressing Enter. The agent's responses will be displayed in the terminal.

## Running the API Server

The `api_server.py` file starts an HTTP API server that allows you to interact with the agent service through API calls.  To run the server, use the following command:
```
bash
python api_server.py
```
The server will start and listen for requests on the default port (typically 8000).  You will see a message indicating the server is running, for example:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
## Making API Calls

Once the API server is running, you can use tools like `curl` to make requests to it.  The primary endpoint is `/chat`, which accepts POST requests with a JSON body containing the user's message.

Here's an example `curl` command:
```
bash
curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello, agent!"}' http://localhost:8000/chat
```
This command sends the message "Hello, agent!" to the server. The server will respond with a JSON object containing the agent's response.  For example:
```
json
{"response": "Hello there! How can I assist you today?"}
```
## Important Notes

*   Ensure that the virtual environment is activated before running either the client or the server.
*   The API server runs on port 8000 by default.  If you need to use a different port, you may need to modify the `api_server.py` code.
*   The terminal client and API server can be run simultaneously to provide multiple ways of interacting with the agent service.