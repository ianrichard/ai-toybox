import os
import json
import logging

logger = logging.getLogger("server.utils.mcp_config")

DEFAULT_PATHS = [
    "/app/mcp_config.json",  # Docker
    "./mcp_config.json",     # Local dev/project root
]

def load_mcp_config():
    config_path = os.environ.get("MCP_CONFIG_PATH")
    paths_to_try = [config_path] if config_path else DEFAULT_PATHS
    paths_to_try = [p for p in paths_to_try if p]  # Avoid empty strings

    for path in paths_to_try:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "servers" in data:
                    return data["servers"]
        except Exception as e:
            logger.info(f"Tried MCP config path {path}: {e}")

    logger.error(
        f"Could not load MCP config file. Paths tried: {paths_to_try}. "
        "Set MCP_CONFIG_PATH environment variable or ensure mcp_config.json is present."
    )
    return []