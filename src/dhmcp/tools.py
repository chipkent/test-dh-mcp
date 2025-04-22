"""
tools.py

Defines tools that can be registered with the MCP server instance (mcp_server).
All tools should use the @mcp_server.tool() decorator.
"""

import logging
from .server import mcp_server


@mcp_server.tool()
def echo_tool(message: str) -> str:
    """
    Echo tool that returns the input message prefixed with 'Echo:'.

    Args:
        message (str): The message to echo back.

    Returns:
        str: The echoed message, prefixed with 'Echo: '.
    """
    result = f"Echo: {message}"
    logging.info("echo_tool called with message: %r, returning: %r", message, result)
    return result

@mcp_server.tool()
def gnome_count_colorado() -> int:
    """
    Returns the current number of gnomes in Colorado.

    Returns:
        int: The number of gnomes.
    """
    count = 53
    logging.info("gnome_count_colorado called, returning: %d", count)
    return count
