"""Main entry point for SmartHub MCP."""
from mcp.server import run_server
from .server import SmartHubMCPServer

def main():
    """Run the SmartHub MCP server."""
    run_server(SmartHubMCPServer)

if __name__ == "__main__":
    main()
