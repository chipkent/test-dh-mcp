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
import os
from mcp.server.fastmcp import FastMCP
from pydeephaven import Session

mcp_server = FastMCP("test-dh-mcp")

def _get_session() -> Session:
    """
    Create and return a configured Deephaven Session.

    The session is configured using the following environment variables:
        - DH_MCP_HOST: Hostname or IP address of the Deephaven server (default: None)
        - DH_MCP_PORT: Port number for the Deephaven server (default: None)
        - DH_MCP_AUTH_TYPE: Authentication type (default: 'Anonymous')
        - DH_MCP_AUTH_TOKEN: Authentication token (default: '')
        - DH_MCP_NEVER_TIMEOUT: Whether the session should never timeout (default: True)
        - DH_MCP_SESSION_TYPE: Session type, e.g., 'python' (default: 'python')
        - DH_MCP_USE_TLS: Whether to use TLS/SSL (default: False)
        - DH_MCP_TLS_ROOT_CERTS: Path to TLS root certificates (default: None)
        - DH_MCP_CLIENT_CERT_CHAIN: Path to client certificate chain (default: None)
        - DH_MCP_CLIENT_PRIVATE_KEY: Path to client private key (default: None)
        - DH_MCP_CLIENT_OPTS: Additional client options (default: None)
        - DH_MCP_EXTRA_HEADERS: Extra headers to include in the session (default: None)

    Returns:
        Session: A configured Deephaven Session instance.
    """

    host = os.getenv("DH_MCP_HOST", None)
    port = os.getenv("DH_MCP_PORT", None)
    auth_type = os.getenv("DH_MCP_AUTH_TYPE", "Anonymous")
    auth_token = os.getenv("DH_MCP_AUTH_TOKEN", "")
    never_timeout = os.getenv("DH_MCP_NEVER_TIMEOUT", True)
    session_type = os.getenv("DH_MCP_SESSION_TYPE", "python")
    use_tls = os.getenv("DH_MCP_USE_TLS", False)
    tls_root_certs = os.getenv("DH_MCP_TLS_ROOT_CERTS", None)
    client_cert_chain = os.getenv("DH_MCP_CLIENT_CERT_CHAIN", None)
    client_private_key = os.getenv("DH_MCP_CLIENT_PRIVATE_KEY", None)

    logging.info(
        "Creating Deephaven Session with: host=%r, port=%r, auth_type=%r, never_timeout=%r, session_type=%r, use_tls=%r, tls_root_certs=%s, client_cert_chain=%s, client_private_key=%s",
        host, port, auth_type, never_timeout, session_type, use_tls,
        "REDACTED" if tls_root_certs else None,
        "REDACTED" if client_cert_chain else None,
        "REDACTED" if client_private_key else None,
    )
    if auth_token:
        logging.info("Auth token: REDACTED")

    try:
        return Session(
            host=host, 
            port=port,
            auth_type=auth_type,
            auth_token=auth_token,
            never_timeout=never_timeout,
            session_type=session_type,
            use_tls=use_tls,
            tls_root_certs=tls_root_certs,
            client_cert_chain=client_cert_chain,
            client_private_key=client_private_key,
           )
    except Exception as e:
        logging.error(f"Failed to create Deephaven session: {e}")
        raise

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
def pydeephaven_list_tables() -> list:
    """
    Connect to a Deephaven server using pydeephaven and return the list of table names in the session.

    Deephaven connection parameters are configured via the following environment variables:
        - DH_MCP_HOST: Hostname or IP address of the Deephaven server (default: None)
        - DH_MCP_PORT: Port number for the Deephaven server (default: None)
        - DH_MCP_AUTH_TYPE: Authentication type (default: 'Anonymous')
        - DH_MCP_AUTH_TOKEN: Authentication token (default: '')
        - DH_MCP_NEVER_TIMEOUT: Whether the session should never timeout (default: True)
        - DH_MCP_SESSION_TYPE: Session type, e.g., 'python' (default: 'python')
        - DH_MCP_USE_TLS: Whether to use TLS/SSL (default: False)
        - DH_MCP_TLS_ROOT_CERTS: Path to TLS root certificates (default: None)
        - DH_MCP_CLIENT_CERT_CHAIN: Path to client certificate chain (default: None)
        - DH_MCP_CLIENT_PRIVATE_KEY: Path to client private key (default: None)
        - DH_MCP_CLIENT_OPTS: Additional client options (default: None)
        - DH_MCP_EXTRA_HEADERS: Extra headers to include in the session (default: None)

    Returns:
        list: List of table names available in the session.
    """

    try:
        with _get_session() as session:
            logging.info(f"Session created successfully for host: {session.host}")
            tables = list(session.tables)
            logging.info(f"Retrieved tables from session: {tables!r}")
            logging.info(f"Session closed for host: {session.host}")
            logging.info(f"pydeephaven_list_tables returning tables: {tables!r}")
            return tables
    except Exception as e:
        #TODO: this is returning with isError=False
        logging.error(f"pydeephaven_list_tables failed for host: {e!r}", exc_info=True)
        return [f"Error: {e}"]

@mcp_server.tool()
def pydeephaven_table_schemas() -> list:
    """
    Connect to a Deephaven server using pydeephaven and return the names and schemas of all tables in the session.

    Deephaven connection parameters are configured via the following environment variables:
        - DH_MCP_HOST: Hostname or IP address of the Deephaven server (default: None)
        - DH_MCP_PORT: Port number for the Deephaven server (default: None)
        - DH_MCP_AUTH_TYPE: Authentication type (default: 'Anonymous')
        - DH_MCP_AUTH_TOKEN: Authentication token (default: '')
        - DH_MCP_NEVER_TIMEOUT: Whether the session should never timeout (default: True)
        - DH_MCP_SESSION_TYPE: Session type, e.g., 'python' (default: 'python')
        - DH_MCP_USE_TLS: Whether to use TLS/SSL (default: False)
        - DH_MCP_TLS_ROOT_CERTS: Path to TLS root certificates (default: None)
        - DH_MCP_CLIENT_CERT_CHAIN: Path to client certificate chain (default: None)
        - DH_MCP_CLIENT_PRIVATE_KEY: Path to client private key (default: None)
        - DH_MCP_CLIENT_OPTS: Additional client options (default: None)
        - DH_MCP_EXTRA_HEADERS: Extra headers to include in the session (default: None)

    Returns:
        list: List of dicts with table name and schema (list of column name/type pairs).
    Example return value:
        [
            {"table": "t1", "schema": [{"name": "C1", "type": "int"}, ...]},
            ...
        ]
    """

    results = []
    try:
        with _get_session() as session:
            logging.info(f"Session created successfully for host: {session.host}")
            for table in session.tables:
                meta_table = session.open_table(table).meta_table.to_arrow()
                print(meta_table)

                # meta_table is a pyarrow.Table with columns: 'Name', 'DataType', etc.
                schema = {row["Name"]: row["DataType"] for row in meta_table.to_pylist()}
                results.append({"table": table, "schema": schema})
            logging.info(f"pydeephaven_table_schemas returning: {results!r}")
            return results
    except Exception as e:
        logging.error(f"pydeephaven_table_schemas failed for host: {e!r}", exc_info=True)
        return [f"Error: {e}"]
