"""SmartHub MCP Extension."""
from mcp import Server
from .server import SmartHubServer

def main():
    """Run the SmartHub MCP server."""
    server = SmartHubServer()
    server.run()

Server = SmartHubServer
