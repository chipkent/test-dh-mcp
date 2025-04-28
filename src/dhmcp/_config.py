"""
Configuration management for Deephaven worker servers.

This module provides centralized logic for loading, validating, and accessing
Deephaven worker configuration from a JSON file, as specified by the
DH_MCP_CONFIG_FILE environment variable. It ensures robust error handling,
strict schema validation, and provides helpers for retrieving worker names
and the default worker.

Main Features:
- Loads and caches configuration from a JSON file.
- Validates config structure and required/allowed fields.
- Provides access to individual worker configs and worker lists.
- Enforces that only 'workers' and 'default_worker' are top-level keys.
- Designed for use by other modules and tools in the dhmcp package.
"""

import os
import json
import logging
from typing import Optional, Dict, Any

_CONFIG_CACHE: Optional[Dict[str, Any]] = None
"""
Cache for the loaded Deephaven worker configuration.
Type: Optional[Dict[str, Any]]
"""

CONFIG_ENV_VAR = "DH_MCP_CONFIG_FILE"
"""
The name of the environment variable that specifies the path to the worker config file.
Type: str
"""

_REQUIRED_FIELDS = []
"""
List of required fields for each worker configuration.
Type: list[str]
"""

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
"""
Dictionary of allowed worker configuration fields and their expected types.
Type: dict[str, type | tuple[type, ...]]
"""

def _load_config() -> Dict[str, Any]:
    """
    Loads and validates the Deephaven worker configuration from the path specified by the DH_MCP_CONFIG_FILE environment variable.

    Returns:
        Dict[str, Any]: The loaded and validated configuration dictionary.

    Raises:
        RuntimeError: If the environment variable is not set or the file cannot be read.
        ValueError: If the config file is not a JSON object (dict), contains unknown keys, or fails validation.
    """
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None:
        logging.debug("Using cached Deephaven worker configuration.")
        return _CONFIG_CACHE

    logging.info("Loading Deephaven worker configuration...")
    config_path = os.environ.get(CONFIG_ENV_VAR)
    if not config_path:
        logging.error(f"Environment variable {CONFIG_ENV_VAR} must be set to the path of the Deephaven worker config file.")
        raise RuntimeError(f"Environment variable {CONFIG_ENV_VAR} must be set to the path of the Deephaven worker config file.")

    logging.info(f"Loading config from: {config_path}")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load Deephaven config from {config_path}: {e}")
        raise RuntimeError(f"Failed to load config file {config_path}: {e}")

    logging.info("Successfully loaded Deephaven worker configuration.")

    if not isinstance(config, dict):
        raise ValueError(f"Config file {config_path} is not a JSON object (dict).")

    # Only allow 'workers' and 'default_worker' as top-level keys
    allowed_config_keys = {'workers', 'default_worker'}
    for key in config:
        if key not in allowed_config_keys:
            raise ValueError(f"Config file {config_path} contains unknown top-level key: '{key}'. Allowed keys are: {sorted(allowed_config_keys)}.")

    workers = config.get("workers")
    if not isinstance(workers, dict) or not workers:
        raise ValueError(f"Config file {config_path} must contain a non-empty 'workers' dictionary.")

    # Validate that default_worker, if present, is a key in workers
    default_worker = config.get("default_worker")
    if default_worker is not None and default_worker not in workers:
        raise ValueError(
            f"Config file {config_path}: default_worker '{default_worker}' is not a key in the workers dictionary."
        )

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
                    raise ValueError(
                        f"Field '{field}' in worker '{key}' config should be of type {expected_type}, got {type(value)}."
                    )

    logging.info("Successfully loaded Deephaven worker configuration.")

    _CONFIG_CACHE = config
    return _CONFIG_CACHE


def get_worker_config(worker_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve the configuration dictionary for a specified worker.

    Args:
        worker_name (Optional[str]): The name of the worker. If None, uses the default_worker from config.

    Returns:
        Dict[str, Any]: The configuration dictionary for the specified worker.

    Raises:
        RuntimeError: If no workers are defined, or if the worker is not found and no default_worker is set.
    """
    config = _load_config()
    workers = config.get("workers", {})

    # Validate that workers exist and are a dictionary
    if not workers or not isinstance(workers, dict):
        raise RuntimeError("No workers defined in Deephaven config file, or workers is not a dictionary.")

    # Determine which worker name to use
    resolved_worker = worker_name or config.get("default_worker")
    if not resolved_worker:
        raise RuntimeError("No worker name specified (via argument or default_worker in config).")

    # Check that the resolved worker exists
    if resolved_worker not in workers:
        raise RuntimeError(f"Worker '{resolved_worker}' not found in config.")

    return workers[resolved_worker]

def deephaven_worker_names() -> list[str]:
    """
    Returns a list of all configured Deephaven worker names from the configuration.

    Returns:
        list[str]: List of Deephaven worker names.
    """

    config = _load_config()
    workers = config.get("workers", {})
    return list(workers.keys())

def deephaven_default_worker() -> Optional[str]:
    """
    Returns the name of the default Deephaven worker, if set in the configuration.

    Returns:
        Optional[str]: The default worker name, or None if not set.
    """

    config = _load_config()
    return config.get("default_worker")
