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
import os
import json
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from pydeephaven import Session

#TODO: add worker session caching
#TODO: add a tool to reload / refresh the configuration / search for new servers

# --- Configuration Loading ---

_CONFIG_CACHE: Optional[Dict[str, Any]] = None

CONFIG_ENV_VAR = "DH_MCP_CONFIG_FILE"


def _load_config() -> Dict[str, Any]:
    """
    Load the Deephaven worker configuration from the path specified by the DH_MCP_CONFIG_FILE environment variable.
    This environment variable is required. If it is not set, an error is raised.
    """
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = os.environ.get(CONFIG_ENV_VAR)

    if not config_path:
        raise RuntimeError(f"Environment variable {CONFIG_ENV_VAR} must be set to the path of the Deephaven worker config file.")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load Deephaven config from {config_path}: {e}")
        raise

    # --- Validation ---
    if not isinstance(config, dict):
        raise ValueError(f"Config file {config_path} is not a JSON object.")

    workers = config.get("workers")

    if not isinstance(workers, dict) or not workers:
        raise ValueError(f"Config file {config_path} must contain a non-empty 'workers' dictionary.")

    # Validate that default_worker, if present, is a key in workers
    default_worker = config.get("default_worker")

    if default_worker is not None and default_worker not in workers:
        raise ValueError(f"Config file {config_path}: default_worker '{default_worker}' is not a key in the workers dictionary.")

    # Allowed fields and their types
    _ALLOWED_WORKER_FIELDS = {
        "host": str,
        "port": int,
        "auth_type": str,
        "auth_token": str,
        "never_timeout": bool,
        "session_type": str,
        "use_tls": bool,
        "tls_root_certs": (str, type(None)),
        "client_cert_chain": (str, type(None)),
        "client_private_key": (str, type(None)),
    }

    # No required fields. All worker fields are optional.
    _REQUIRED_FIELDS = []

    for key, worker_cfg in workers.items():
        if not isinstance(worker_cfg, dict):
            raise ValueError(f"Worker '{key}' in config is not a dictionary.")

        # Check for unknown fields
        for field in worker_cfg:
            if field not in _ALLOWED_WORKER_FIELDS:
                raise ValueError(f"Unknown field '{field}' in worker '{key}' config.")

        # Check for required fields
        for req in _REQUIRED_FIELDS:
            if req not in worker_cfg:
                raise ValueError(f"Missing required field '{req}' in worker '{key}' config.")

        # Check types
        for field, expected_type in _ALLOWED_WORKER_FIELDS.items():
            if field in worker_cfg:
                value = worker_cfg[field]
                if not isinstance(value, expected_type):
                    raise ValueError(f"Field '{field}' in worker '{key}' config should be of type {expected_type}, got {type(value)}.")

    default_worker = config.get("default_worker")

    if default_worker is not None and default_worker not in workers:
        raise ValueError(f"default_worker '{default_worker}' is not a key in the workers dictionary.")

    _CONFIG_CACHE = config
    return _CONFIG_CACHE


def _get_worker_config(worker_name: str = None) -> Dict[str, Any]:
    """
    Retrieve the configuration for the specified worker. If worker_name is None, uses the default_worker from config.
    Raises an error if neither is available or if the worker is not found.
    """
    config = _load_config()
    workers = config.get("workers", {})

    if not workers or not isinstance(workers, dict):
        raise RuntimeError("No workers defined in Deephaven config file, or workers is not a dictionary.")

    # Determine worker name
    name = worker_name or config.get("default_worker")

    if not name:
        raise RuntimeError("No worker name specified (via argument or default_worker in config).")

    if name not in workers:
        raise RuntimeError(f"Worker '{name}' not found in config.")

    return workers[name]


mcp_server = FastMCP("test-dh-mcp")


def _get_session(worker_name: str = None) -> Session:
    """
    Create and return a configured Deephaven Session, using JSON config.
    If worker_name is None, uses the default_worker from config.

    Args:
        worker_name (str, optional): Name of the Deephaven worker to use. If not provided, uses default_worker from config.
    Returns:
        Session: A configured Deephaven Session instance.
    """
    cfg = _get_worker_config(worker_name)
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
        "Creating Deephaven session: host=%r, port=%r, auth_type=%r, never_timeout=%r, session_type=%r, use_tls=%r, tls_root_certs=%s, client_cert_chain=%s, client_private_key=%s",
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
def deephaven_default_worker() -> str:
    """
    Return the name of the default Deephaven worker from the config file to use when a worker name is not specified.

    Returns:
        str: The default worker name
    """
    config = _load_config()
    return config.get("default_worker")


@mcp_server.tool()
def deephaven_worker_names() -> list[str]:
    """
    Return the names of all Deephaven workers defined in the config file.

    Returns:
        list[str]: List of Deephaven worker names.
    """
    config = _load_config()
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

