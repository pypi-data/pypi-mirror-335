"""SmartHub MCP Extension"""
from mcp.server.fastmcp import FastMCP
from .server import SmartHubMCPServer

def main():
    """Run the SmartHub MCP server."""
    server = SmartHubMCPServer()
    server.run()

__version__ = "0.1.0"
