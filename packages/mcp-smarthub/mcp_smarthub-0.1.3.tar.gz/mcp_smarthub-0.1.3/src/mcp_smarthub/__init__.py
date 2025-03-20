"""SmartHub MCP Extension"""
from .server import SmartHubMCPServer

def main():
    """Entry point for the MCP server."""
    server = SmartHubMCPServer()
    server.run()

__version__ = "0.1.3"
