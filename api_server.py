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
    print("WebSocket connection accepted")  # Debug log
    
    try:
        async with AgentService() as service:
            await websocket.send_json({"type": "status", "content": "MCP Ready"})
            print("MCP Ready message sent")  # Debug log
            
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                print(f"Received message: {data}")  # Debug log
                message = json.loads(data)
                
                if message.get("type") == "chat":
                    user_input = message.get("content", "")
                    history = message.get("history", [])
                    print(f"Processing chat message: {user_input}, history: {history}")  # Debug log
                    
                    # Define callbacks for websocket streaming
                    def on_tool_call(tool_call):
                        print(f"Tool call: {tool_call}")  # Debug log
                        asyncio.create_task(
                            websocket.send_json({
                                "type": "tool_call",
                                "content": {"tool_name": tool_call["tool_name"], "args": tool_call["args"]}
                            })
                        )

                    def on_tool_result(result):
                        print(f"Tool result: {result}")  # Debug log
                        asyncio.create_task(
                            websocket.send_json({
                                "type": "tool_result",
                                "content": result
                            })
                        )

                    def on_assistant_message(content):
                        print(f"Assistant message: {content}")  # Debug log
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
                    print(f"Final response: {response}")  # Debug log
                    await websocket.send_json({"type": "final_response", "content": response})
                    
    except WebSocketDisconnect:
        print("WebSocket disconnected")  # Debug log
        pass  # Client disconnected
    except Exception as e:
        print(f"Error in WebSocket handler: {e}")  # Debug log
        await websocket.send_json({"type": "error", "content": str(e)})