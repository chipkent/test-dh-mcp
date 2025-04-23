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

@mcp_server.tool()
def pydeephaven_list_tables(server_url: str = "localhost", port: int = 10000) -> list:
    """
    Connect to a Deephaven server using pydeephaven and return the list of table names in the session.

    Args:
        server_url (str): The URL of the Deephaven server.
        port (int): The port of the Deephaven server.
    Returns:
        list: List of table names available in the session.
    """
    import logging
    from pydeephaven import Session
    logging.info(f"pydeephaven_list_tables called with server_url: {server_url!r}, port: {port!r}")
    try:
        with Session(host=server_url, port=port) as session:
            logging.info(f"Session created successfully for host: {server_url}")
            tables = list(session.tables)
            logging.info(f"Retrieved tables from session: {tables!r}")
            logging.info(f"Session closed for host: {server_url}")
            logging.info(f"pydeephaven_list_tables returning tables: {tables!r}")
            return tables
    except Exception as e:
        #TODO: this is returning with isError=False
        logging.error(f"pydeephaven_list_tables failed for host {server_url}: {e!r}", exc_info=True)
        return [f"Error: {e}"]

@mcp_server.tool()
def pydeephaven_table_schemas(server_url: str = "localhost", port: int = 10000) -> list:
    """
    Connect to a Deephaven server using pydeephaven and return the names and schemas of all tables in the session.

    Args:
        server_url (str): The URL of the Deephaven server.
        port (int): The port of the Deephaven server.
    Returns:
        list: List of dicts with table name and schema (list of column name/type pairs).
    Example return value:
        [
            {"table": "t1", "schema": [{"name": "C1", "type": "int"}, ...]},
            ...
        ]
    """
    import logging
    from pydeephaven import Session
    logging.info(f"pydeephaven_table_schemas called with server_url: {server_url!r}, port: {port!r}")
    results = []
    try:
        with Session(host=server_url, port=port) as session:
            logging.info(f"Session created successfully for host: {server_url}")
            for table in session.tables:
                meta_table = session.open_table(table).meta_table.to_arrow()
                print(meta_table)

                # meta_table is a pyarrow.Table with columns: 'Name', 'DataType', etc.
                schema = {row["Name"]: row["DataType"] for row in meta_table.to_pylist()}
                results.append({"table": table, "schema": schema})
            logging.info(f"pydeephaven_table_schemas returning: {results!r}")
            return results
    except Exception as e:
        logging.error(f"pydeephaven_table_schemas failed for host {server_url}: {e!r}", exc_info=True)
        return [f"Error: {e}"]
