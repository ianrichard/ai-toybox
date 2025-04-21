import os
import logging
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from src.server.agent import AgentService

load_dotenv()

log_level = logging.DEBUG if os.environ.get("DEBUG", "0") in ["1", "true", "True"] else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api.server")

app = FastAPI(title="Pydantic AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="src/client"), name="static")

@app.get("/")
async def get_home():
    return FileResponse("src/client/index.html")

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat")
async def chat(request: ChatRequest):
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
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    try:
        async with AgentService() as service:
            await websocket.send_json({"type": "status", "content": "MCP Ready"})
            logger.info("MCP Ready message sent")
            while True:
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

def run_api(reload=True):
    import uvicorn
    if reload:
        uvicorn.run("src.server.server:app", host="0.0.0.0", port=8000, reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    reload_enabled = os.environ.get('RELOAD', 'True').lower() in ('true', '1', 't')
    run_api(reload=reload_enabled)