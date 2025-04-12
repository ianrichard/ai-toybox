import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
from agent_service import AgentService
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Pydantic AI API")

# Mount static files directory if you have CSS/JS files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Add a route for the root path
@app.get("/")
async def read_root():
    return FileResponse("index.html")

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
    
    try:
        async with AgentService() as service:
            await websocket.send_json({"type": "status", "content": "MCP Ready"})
            
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "chat":
                    user_input = message.get("content", "")
                    
                    # Define callbacks for websocket streaming
                    def on_tool_call(tool_call):
                        asyncio.create_task(
                            websocket.send_json({
                                "type": "tool_call",
                                "content": {"tool_name": tool_call["tool_name"], "args": tool_call["args"]}
                            })
                        )

                    def on_tool_result(result):
                        asyncio.create_task(
                            websocket.send_json({
                                "type": "tool_result",
                                "content": result
                            })
                        )

                    def on_assistant_message(content):
                        asyncio.create_task(
                            websocket.send_json({
                                "type": "assistant",
                                "content": content
                            })
                        )
                    
                    
                    # Process the message and stream the response
                    response = await service.process_input(
                        user_input,
                        on_assistant_message=on_assistant_message,
                        on_tool_call=on_tool_call,
                        on_tool_result=on_tool_result
                    )
                    
                    # Send completion message
                    await websocket.send_json({"type": "final_response", "content": response})
                    
    except WebSocketDisconnect:
        pass  # Client disconnected
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})