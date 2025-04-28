"""
Session management for Deephaven workers.

This module provides thread-safe caching and creation of Deephaven Session objects
based on validated configuration from _config.py. It ensures that sessions are reused
when possible, and only recreated if the previous session is dead or invalid.

Features:
    - Thread-safe session cache keyed by worker name.
    - Automatic session reuse and liveness checking.
    - Loading of certificate files for secure connections.
    - Designed for use by other modules and tools in the dhmcp package.
"""

from typing import Optional
from pydeephaven import Session
from ._config import get_worker_config
import logging

#TODO: add a tool to reload / refresh the configuration / search for new servers

_SESSION_CACHE = {}
_SESSION_CACHE_LOCK = __import__('threading').Lock()
"""
dict: Module-level cache for Deephaven sessions, keyed by worker name (or '__default__').
threading.Lock: Ensures thread-safe access to the session cache.
"""

def get_session(worker_name: Optional[str] = None) -> Session:
    """
    Retrieve a cached or new Deephaven Session for the specified worker.

    If a session for the worker exists in the cache and is alive, it is reused.
    Otherwise, a new session is created, cached, and returned. All access to the
    session cache is thread-safe.

    Args:
        worker_name (str, optional): Name of the Deephaven worker to use. If None,
            uses the default_worker from config.

    Returns:
        Session: A configured, live Deephaven Session instance for the worker.

    Raises:
        RuntimeError: If required configuration fields are missing or invalid.
        Exception: If session creation fails or certificates cannot be loaded.
    """
    # Use worker name as cache key
    resolved_worker = worker_name or None  # None means use default in get_worker_config
    cache_key = resolved_worker or "__default__"

    # First, check and create the session in a single atomic lock block
    with _SESSION_CACHE_LOCK:
        session = _SESSION_CACHE.get(cache_key)
        if session is not None:
            try:
                if session.is_alive():
                    logging.info(f"Returning cached Deephaven session for worker: {resolved_worker}")
                    return session
                else:
                    logging.info(f"Cached Deephaven session for worker '{resolved_worker}' is not alive. Recreating.")
            except Exception as e:
                logging.warning(f"Error checking session liveness for worker '{resolved_worker}': {e}. Recreating session.")

        # At this point, we need to create a new session and update the cache
        cfg = get_worker_config(worker_name)
        host = cfg.get("host", None)
        port = cfg.get("port", None)
        auth_type = cfg.get("auth_type", None)
        auth_token = cfg.get("auth_token", None)
        never_timeout = cfg.get("never_timeout", False)
        session_type = cfg.get("session_type", "python")
        use_tls = cfg.get("use_tls", False)
        tls_root_certs = cfg.get("tls_root_certs", None)
        client_cert_chain = cfg.get("client_cert_chain", None)
        client_private_key = cfg.get("client_private_key", None)

        # Load certificate files as bytes if provided as file paths, with logging (outside lock if slow)
        def _load_bytes(path):
            if path is None:
                return None
            try:
                with open(path, "rb") as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Failed to load certificate/key file: {path}: {e}")
                raise

        if tls_root_certs:
            logging.info(f"Loading TLS root certs from: {cfg.get('tls_root_certs')}")
            tls_root_certs = _load_bytes(tls_root_certs)
            logging.info("Loaded TLS root certs successfully.")
        else:
            logging.info("No TLS root certs provided for session.")
        if client_cert_chain:
            logging.info(f"Loading client cert chain from: {cfg.get('client_cert_chain')}")
            client_cert_chain = _load_bytes(client_cert_chain)
            logging.info("Loaded client cert chain successfully.")
        else:
            logging.info("No client cert chain provided for session.")
        if client_private_key:
            logging.info(f"Loading client private key from: {cfg.get('client_private_key')}")
            client_private_key = _load_bytes(client_private_key)
            logging.info("Loaded client private key successfully.")
        else:
            logging.info("No client private key provided for session.")

        # Redact sensitive info for logging
        log_cfg = dict(cfg)
        if "auth_token" in log_cfg:
            log_cfg["auth_token"] = "<redacted>"
        if "client_private_key" in log_cfg:
            log_cfg["client_private_key"] = "<redacted>"
        if "client_cert_chain" in log_cfg:
            log_cfg["client_cert_chain"] = "<redacted>"
        if "tls_root_certs" in log_cfg:
            log_cfg["tls_root_certs"] = "<redacted>"
        logging.info(f"Creating Deephaven Session with config: {log_cfg} (worker cache key: {cache_key})")

        session = Session(
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
        logging.info(f"Session created for worker '{cache_key}', adding to cache.")
        _SESSION_CACHE[cache_key] = session
        logging.info(f"Session cached for worker '{cache_key}'. Returning session.")
        return session
