import argparse
import asyncio
import logging
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Pydantic AI MCP")
    parser.add_argument(
        "--mode", 
        choices=["api", "cli"], 
        default="cli",
        help="Run mode: api (server) or cli (terminal)"
    )
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
    
    # Run the appropriate interface
    if args.mode == "api":
        from interfaces.api.server import run_api
        run_api()
    else:
        from interfaces.cli.client import run_terminal_interface
        asyncio.run(run_terminal_interface())
        
if __name__ == "__main__":
    main()