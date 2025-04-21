import os
import json
import logging

logger = logging.getLogger("core.utils.config")

DEFAULT_PATHS = [
    "/app/mcp_config.json",  # Docker
    "./mcp_config.json",  # Local dev/project root
]


def load_mcp_config():
    config_path = os.environ.get("MCP_CONFIG_PATH")
    paths_to_try = [config_path] if config_path else DEFAULT_PATHS

    for path in paths_to_try:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "servers" in data:
                    return data["servers"]
        except Exception as e:
            logger.info(f"Tried MCP config path {path}: {e}")

    logger.error(
        "Could not load MCP config file. Set MCP_CONFIG_PATH env variable or ensure mcp_config.json is present."
    )
    return []
