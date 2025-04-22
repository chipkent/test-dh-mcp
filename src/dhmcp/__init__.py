"""
dhmcp package

This package implements the core logic for an MCP (Model Context Protocol) server using FastMCP, and defines all tools available to MCP clients.

Key Features:
- Defines and registers all MCP tools via the `@mcp_server.tool()` decorator.
- Exposes a single `mcp_server` instance for use in your server entry point.
- Designed for easy extension: add new tools by defining functions with appropriate docstrings and decorators.

How to Add Tools:
- Define a new function in this file.
- Decorate it with `@mcp_server.tool()`.
- Write a clear docstring describing its arguments and return value.

Usage:
- Import `mcp_server` in your server entry point (e.g., `mcp_server.py`) and call `mcp_server.run()`.
- Use the provided client script or MCP Inspector to discover and invoke tools.

Example:
    from dhmcp import mcp_server

Available Tools:
- echo_tool: Echoes a message back to the caller.
- gnome_count_colorado: Returns the number of gnomes in Colorado.

See the project README for more information on running the server and interacting with tools.
"""

import logging
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("test-dh-mcp")

@mcp_server.tool()
def echo_tool(message: str) -> str:
    """
    Echo the input message, prefixed with 'Echo: '.

    Args:
        message (str): The message to echo back to the caller.

    Returns:
        str: The echoed message, prefixed with 'Echo: '.
    """
    result = f"Echo: {message}"
    logging.info("echo_tool called with message: %r, returning: %r", message, result)
    return result

@mcp_server.tool()
def gnome_count_colorado() -> int:
    """
    Return the current number of gnomes in Colorado.

    Returns:
        int: The number of gnomes in Colorado.
    """
    count = 53
    logging.info("gnome_count_colorado called, returning: %d", count)
    return count
