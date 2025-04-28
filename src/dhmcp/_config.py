import os
import json
import logging
from typing import Optional, Dict, Any

_CONFIG_CACHE: Optional[Dict[str, Any]] = None
CONFIG_ENV_VAR = "DH_MCP_CONFIG_FILE"

# No required fields. All worker fields are optional.
_REQUIRED_FIELDS = []

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

def load_config() -> Dict[str, Any]:
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
        raise RuntimeError(f"Failed to load config file {config_path}: {e}")

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

    _CONFIG_CACHE = config
    return _CONFIG_CACHE


def get_worker_config(worker_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve the configuration for the specified worker. If worker_name is None, uses the default_worker from config.
    Raises an error if neither is available or if the worker is not found.
    """
    config = load_config()
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

def deephaven_worker_names() -> list[str]:
    config = load_config()
    workers = config.get("workers", {})
    return list(workers.keys())

def deephaven_default_worker() -> Optional[str]:
    config = load_config()
    return config.get("default_worker")
