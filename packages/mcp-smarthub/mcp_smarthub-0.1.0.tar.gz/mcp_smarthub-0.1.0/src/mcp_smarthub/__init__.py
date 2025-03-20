"""SmartHub MCP Extension"""
from mcp.server import run_server
from .server import SmartHubMCPServer

def main():
    """Run the SmartHub MCP server."""
    run_server(SmartHubMCPServer)

__version__ = "0.1.0"
