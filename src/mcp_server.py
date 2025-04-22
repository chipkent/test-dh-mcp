"""
mcp_server.py

Main entry point for running the MCP (Model Context Protocol) server.

- This script configures logging and starts the MCP server instance (`mcp_server`).
- All tools and endpoints should be registered via decorators in `dhmcp/tools.py`.
- To add or modify tools, edit `dhmcp/tools.py` and use the `@mcp_server.tool()` decorator.
- To run the server, execute this script directly or with `PYTHONPATH=./src python src/mcp_server.py`.
- The server uses SSE (Server-Sent Events) transport by default for compatibility with MCP clients.

Example:
    $ PYTHONPATH=./src python src/mcp_server.py

For more information, see the project README.
"""

import logging
from dhmcp import mcp_server

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
logging.getLogger("mcp").setLevel(logging.DEBUG)

if __name__ == "__main__":
    transport = "sse"
    logging.info(f"Starting MCP server '{mcp_server.name}' with transport={transport}")
    try:
        mcp_server.run(transport=transport)
    finally:
        logging.info(f"MCP server '{mcp_server.name}' stopped.")
