import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import logging
from agent_service import AgentService
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Set up proper logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_server")

app = FastAPI(title="Pydantic AI API")

# Mount the entire api-test-app directory as static files
app.mount("/api-test-app", StaticFiles(directory="api-test-app"), name="api-test-app")

# Also mount static files at root for backward compatibility
app.mount("/css", StaticFiles(directory="api-test-app/css"), name="css")
app.mount("/js", StaticFiles(directory="api-test-app/js"), name="js")

# Add a route for the root path to serve the original index.html for backward compatibility
@app.get("/")
async def read_root():
    return FileResponse("api-test-app/index.html")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    content: str
    tool_calls: list
    tool_results: list

@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """Stream chat responses through WebSocket"""
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
    """Handle a chat message from the client"""
    user_input = message.get("content", "")
    history = message.get("history", [])
    logger.debug(f"Processing chat message: {user_input}, history: {history}")
    
    # Define callbacks for websocket streaming
    def on_tool_call(tool_call):
        logger.debug(f"Tool call: {tool_call}")
        asyncio.create_task(
            websocket.send_json({
                "type": "tool_call",
                "content": {"tool_name": tool_call["tool_name"], "args": tool_call["args"]}
            })
        )

    def on_tool_result(result):
        logger.debug(f"Tool result: {result}")
        asyncio.create_task(
            websocket.send_json({
                "type": "tool_result",
                "content": result
            })
        )

    def on_assistant_message(content):
        logger.debug(f"Assistant message: {content}")
        asyncio.create_task(
            websocket.send_json({
                "type": "assistant",
                "content": content
            })
        )
    
    # Process the message and stream the response
    response = await service.process_input(
        user_input,
        history=history,
        on_assistant_message=on_assistant_message,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result
    )
    
    # Send completion message
    logger.debug(f"Final response: {response}")
    await websocket.send_json({"type": "final_response", "content": response})