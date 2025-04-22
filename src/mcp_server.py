"""
mcp_server.py

Main entry point for running the MCP (Model Context Protocol) server.

- This script configures logging and starts the MCP server instance (`mcp_server`).
- The transport type can be set with the `--transport` command line argument (default: 'sse').
- If transport is 'stdio', logging is set to ERROR for minimal output.
- All tools should be registered via decorators in `dhmcp/__init__.py`.
- To run the server, execute this script directly or with `PYTHONPATH=./src python src/mcp_server.py [--transport sse|stdio]`.

Example:
    $ PYTHONPATH=./src python src/mcp_server.py --transport stdio
    $ PYTHONPATH=./src python src/mcp_server.py  # (defaults to sse)

For more information, see the project README.
"""

import logging
import argparse
from dhmcp import mcp_server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MCP server.")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio"],
        default="sse",
        help="Transport type for the MCP server (default: sse)"
    )
    args = parser.parse_args()
    transport = args.transport

    log_level = logging.ERROR if transport == "stdio" else logging.DEBUG
    logging.basicConfig(level=log_level, format='[%(asctime)s] %(levelname)s: %(message)s')
    logging.getLogger("mcp").setLevel(log_level)

    logging.info(f"Starting MCP server '{mcp_server.name}' with transport={transport}")
    try:
        mcp_server.run(transport=transport)
    finally:
        logging.info(f"MCP server '{mcp_server.name}' stopped.")
