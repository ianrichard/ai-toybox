from fastmcp import FastMCP, Client
from fastmcp.client.transports import PythonStdioTransport, StdioTransport
import json
import sys


# --- Aggregate/Composite MCP ---
mcp = FastMCP("Aggregated MCP Server")

def load_and_mount_servers(config):
    servers = []
    for server_config in config.get("servers", []):
        name = server_config["name"]
        transport = server_config["transport"]
        command = [transport["command"]] + transport.get("args", [])
        print(f"Mounting subprocess MCP: {name} ({' '.join(command)})", file=sys.stderr)
        if command[0].endswith(".py"):
            client = Client(transport=PythonStdioTransport(command[0]))
        else:
            client = Client(transport=StdioTransport(command[0], command[1:]))
        proxy = FastMCP.from_client(client, name=name)
        mcp.mount(name, proxy)
        servers.append(client)
    return servers

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "mcp_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    servers = load_and_mount_servers(config)
    return servers

if __name__ == "__main__":
    servers = main()
    mcp.run()