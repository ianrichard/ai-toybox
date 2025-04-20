import os
import json
import logging

logger = logging.getLogger("core.utils.config")

def load_mcp_config():
    config_path = os.environ.get("MCP_CONFIG_PATH", "/app/mcp_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "servers" in data:
                return data["servers"]
    except Exception as e:
        logger.error(f"Could not load MCP config from {config_path}: {e}")
    return []