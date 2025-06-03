"""MCP Server - Claude Desktop Integration

This module serves as a thin wrapper around server.py for backward compatibility.
It imports the MCP server instance from server.py and runs it when executed directly.
"""

import sys
from server import create_mcp_server

mcp = create_mcp_server()

if __name__ == "__main__":
    try:
        print("Starting MCP server...", file=sys.stderr)
        mcp.run()
    except Exception as e:
        print("Startup error:", e, file=sys.stderr)
        raise
