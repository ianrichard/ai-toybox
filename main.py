import asyncio
import sys
import uvicorn

def start_terminal():
    """Start the application in terminal mode."""
    from terminal_client import run_terminal_interface
    asyncio.run(run_terminal_interface())

def start_api(host="0.0.0.0", port=8000):
    """Start the application in API server mode."""
    from api_server import app
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Pydantic AI MCP Client')
    parser.add_argument('--mode', choices=['terminal', 'api'], default='terminal',
                        help='Run in terminal mode or as API server')
    parser.add_argument('--host', default='0.0.0.0', help='API server host (for API mode)')
    parser.add_argument('--port', type=int, default=8000, help='API server port (for API mode)')
    
    args = parser.parse_args()
    
    if args.mode == 'terminal':
        start_terminal()
    else:
        start_api(host=args.host, port=args.port)