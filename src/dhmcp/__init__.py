"""
dhmcp package

This package implements the core logic for an MCP (Model Context Protocol) server using FastMCP, and defines all tools available to MCP clients.

Configuration:
- All Deephaven worker connection information is managed via a JSON configuration file (default: `deephaven_workers.json` in the project root, or set with the `DH_MCP_CONFIG_FILE` environment variable).
- The config file must contain a `workers` dictionary, keyed by worker name, with each value a dictionary of connection parameters (see README for schema).
- Strict validation is performed on config load: only allowed fields are permitted and all fields must be the correct type. All worker fields are optional; define only those needed for your deployment.
- The config may also specify a `default_worker` key, which names the default worker for UI or documentation purposes, but all API calls require an explicit worker name.

How to Add Tools:
- Define a new function in this file.
- Decorate it with `@mcp_server.tool()`.
- Write a clear docstring describing its arguments and return value.

Usage:
- Import `mcp_server` in your server entry point (e.g., `mcp_server.py`) and call `mcp_server.run()`.
- Use the provided client script or MCP Inspector to discover and invoke tools.
- Use `deephaven_worker_names()` to enumerate available workers, and pass the desired worker name to any tool that requires it.

Available Tools:
- `echo_tool(message: str) -> str`: Echoes a message back to the caller.
- `gnome_count_colorado() -> int`: Returns the number of gnomes in Colorado.
- `deephaven_worker_names() -> list[str]`: Returns all configured Deephaven worker names.
- `deephaven_list_tables(worker_name: str) -> list`: Lists tables for the specified Deephaven worker.
- `deephaven_table_schemas(worker_name: str) -> list`: Returns schemas for all tables in the specified Deephaven worker.

See the project README for more information on configuration, running the server, and interacting with tools.
"""

import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from pydeephaven import Session
from ._config import load_config, get_worker_config, deephaven_worker_names, deephaven_default_worker

#TODO: add worker session caching
#TODO: add a tool to reload / refresh the configuration / search for new servers

mcp_server = FastMCP("test-dh-mcp")


def _get_session(worker_name: Optional[str] = None) -> Session:
    """
    Create and return a configured Deephaven Session, using JSON config.
    If worker_name is None, uses the default_worker from config.

    Args:
        worker_name (str, optional): Name of the Deephaven worker to use. If not provided, uses default_worker from config.
    Returns:
        Session: A configured Deephaven Session instance.
    """
    cfg = get_worker_config(worker_name)
    host = cfg.get("host", None)
    port = cfg.get("port", None)
    auth_type = cfg.get("auth_type", "Anonymous")
    auth_token = cfg.get("auth_token", "")
    never_timeout = cfg.get("never_timeout", True)
    session_type = cfg.get("session_type", "python")
    use_tls = cfg.get("use_tls", False)
    tls_root_certs = cfg.get("tls_root_certs", None)
    client_cert_chain = cfg.get("client_cert_chain", None)
    client_private_key = cfg.get("client_private_key", None)

    if not host or not port:
        raise RuntimeError(f"Worker config must specify 'host' and 'port'. Got: {cfg}")

    logging.info(
        "Creating Deephaven session: host=%r, port=%r, auth_type=%r, auth_token=%r, never_timeout=%r, session_type=%r, use_tls=%r, tls_root_certs=%s, client_cert_chain=%s, client_private_key=%s",
        host, port, auth_type, "REDACTED", never_timeout, session_type, use_tls,
        tls_root_certs, client_cert_chain, client_private_key,
    )

    # Load cert/key files as bytes if paths are provided
    def _load_bytes(path):
        if path is None:
            return None
        try:
            with open(path, "rb") as f:
                return f.read()
        except Exception as e:
            logging.error(f"Failed to load file '{path}': {e}")
            raise

    try:
        return Session(
            host=host,
            port=port,
            auth_type=auth_type,
            auth_token=auth_token,
            never_timeout=never_timeout,
            session_type=session_type,
            use_tls=use_tls,
            tls_root_certs=_load_bytes(tls_root_certs) if tls_root_certs else None,
            client_cert_chain=_load_bytes(client_cert_chain) if client_cert_chain else None,
            client_private_key=_load_bytes(client_private_key) if client_private_key else None,
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
def deephaven_default_worker() -> str:
    """
    Return the name of the default Deephaven worker from the config file to use when a worker name is not specified.

    Returns:
        str: The default worker name
    """
    config = load_config()
    return config.get("default_worker")


@mcp_server.tool()
def deephaven_worker_names() -> list[str]:
    """
    Return the names of all Deephaven workers defined in the config file.

    Returns:
        list[str]: List of Deephaven worker names.
    """
    config = load_config()
    workers = config.get("workers", {})
    return list(workers.keys())


@mcp_server.tool()
def deephaven_list_tables(worker_name: Optional[str] = None) -> list:
    """
    Returns a list of table names available in the specified Deephaven worker.
    If no worker_name is provided, uses the default worker from config.

    Args:
        worker_name (str, optional): Name of the Deephaven worker to use. If not provided, uses default_worker from config.
    Returns:
        list: List of table names available in the Deephaven worker.
    """
    try:
        with _get_session(worker_name) as session:
            logging.info(f"deephaven_list_tables: Session created successfully for worker: {worker_name or deephaven_default_worker()}")
            tables = list(session.tables)
            logging.info(f"deephaven_list_tables: Retrieved tables from session: {tables!r}")
            logging.info(f"deephaven_list_tables: returning tables: {tables!r}")
            return tables
    except Exception as e:
        logging.error(f"deephaven_list_tables failed for worker: {worker_name or deephaven_default_worker()}, error: {e!r}", exc_info=True)
        return [f"Error: {e}"]


@mcp_server.tool()
def deephaven_table_schemas(worker_name: Optional[str] = None) -> list:
    """
    Returns the names and schemas of all tables in the specified Deephaven worker.
    If no worker_name is provided, uses the default worker from config.

    Args:
        worker_name (str, optional): Name of the Deephaven worker to use. If not provided, uses default_worker from config.
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
        with _get_session(worker_name) as session:
            logging.info(f"deephaven_table_schemas: Session created successfully for worker: {worker_name or deephaven_default_worker()}")

            for table in session.tables:
                meta_table = session.open_table(table).meta_table.to_arrow()
                # meta_table is a pyarrow.Table with columns: 'Name', 'DataType', etc.
                schema = {row["Name"]: row["DataType"] for row in meta_table.to_pylist()}
                results.append({"table": table, "schema": schema})

            logging.info(f"deephaven_table_schemas: returning: {results!r}")
            return results
    except Exception as e:
        logging.error(f"deephaven_table_schemas: failed for worker: {worker_name or deephaven_default_worker()}, error: {e!r}", exc_info=True)
        return [f"Error: {e}"]

