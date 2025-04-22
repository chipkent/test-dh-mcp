"""
server.py

This module configures and runs the MCP server instance (mcp_server).

- All tools should be registered via decorators in other modules (e.g., tools.py).
- Run this file as a script or module to start the MCP server.
"""

import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

mcp_server = FastMCP("My MCP Server")

if __name__ == "__main__":
    logging.info("Starting MCP server '%s' with transport=sse", getattr(mcp_server, 'name', 'unnamed'))
    try:
        mcp_server.run(transport="sse")
    finally:
        logging.info("MCP server stopped.")
