import argparse
import asyncio
import logging
import os
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json

from chat.agent import AgentService

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Pydantic AI MCP")
parser.add_argument(
    "--debug", 
    action="store_true",
    help="Enable debug logging"
)
args = parser.parse_args()

# Configure logging
log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api.server")

app = FastAPI(title="Pydantic AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for the web client
app.mount("/static", StaticFiles(directory="src/chat/web_client"), name="static")

@app.get("/")
async def get_home():
    """Serve the home page."""
    return FileResponse("src/chat/web_client/index.html")

class ChatRequest(BaseModel):
    """Model for chat requests."""
    message: str
    history: list = []

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Process a chat message via REST API."""
    logger.info(f"Received chat request: {request.message[:50]}...")
    
    try:
        async with AgentService() as service:
            response = await service.process_input(
                request.message,
                history=request.history
            )
            return response
    except Exception as e:
        logger.exception(f"Error in chat endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """Stream chat responses through WebSocket."""
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    try:
        async with AgentService() as service:
            await websocket.send_json({"type": "status", "content": "MCP Ready"})
            logger.info("MCP Ready message sent")
            
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                logger.debug(f"Received message: {data}")
                
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON: {data}")
                    await websocket.send_json({"type": "error", "content": "Invalid JSON"})
                    continue
                
                if message.get("type") == "chat":
                    await handle_chat_message(websocket, service, message)
                else:
                    logger.warning(f"Unknown message type: {message.get('type')}")
                    await websocket.send_json({"type": "error", "content": "Unknown message type"})
                    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.exception(f"Error in WebSocket handler: {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            logger.error("Failed to send error message, connection might be closed")


async def handle_chat_message(websocket: WebSocket, service: AgentService, message: dict):
    """Handle a chat message from the client."""
    user_input = message.get("content", "")
    history = message.get("history", [])
    logger.info(f"Processing chat: '{user_input[:50]}...'")
    
    async def send_websocket_json(msg_type, content, complete=False):
        try:
            await websocket.send_json({
                "type": msg_type,
                "content": content,
                "complete": complete
            })
        except Exception as e:
            logger.error(f"Failed to send {msg_type}: {e}")
    
    # Define callbacks for websocket streaming
    def on_tool_call(tool_call):
        logger.debug(f"Tool call: {tool_call}")
        asyncio.create_task(websocket.send_json(tool_call))

    def on_tool_result(result):
        logger.debug(f"Tool result: {str(result)[:100]}...")
        asyncio.create_task(websocket.send_json(result))

    def on_assistant_message(content):
        asyncio.create_task(send_websocket_json("assistant", content))
    
    response = await service.process_input(
        user_input,
        history=history,
        on_assistant_message=on_assistant_message,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result
    )
    
    logger.info(f"Chat completed: {len(response.get('assistant_content', ''))} chars")
    await send_websocket_json("assistant", "", complete=True)
    
def run_api(reload=True):  # Default to True for development
    """Run the API server."""
    import uvicorn
    
    if reload:
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    reload_enabled = os.environ.get('RELOAD', 'True').lower() in ('true', '1', 't')
    run_api(reload=reload_enabled)