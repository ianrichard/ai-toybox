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
    
    # Always run API mode
    from interfaces.api.server import run_api
    reload_enabled = os.environ.get('RELOAD', 'True').lower() in ('true', '1', 't')
    run_api(reload=reload_enabled)
        
if __name__ == "__main__":
    main()