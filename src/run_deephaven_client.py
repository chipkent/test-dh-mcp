
"""
run_deephaven_client.py
----------------------
This script connects to a running Deephaven server instance using the pydeephaven client, retrieves the list of available tables, and prints them to stdout.

Usage:
    uv run ./src/run_deephaven_client.py

Requirements:
    - Deephaven server running and accessible at the specified host and port
    - pydeephaven Python package installed

Environment:
    - server_url: Hostname or IP address of the Deephaven server (default: 'localhost')
    - port: Port number for the Deephaven server (default: 10000)
"""

import logging
from pydeephaven import Session

# Configuration for Deephaven server connection
server_url = "localhost"
port = 10000

# Log the start of the table listing operation
logging.info(f"pydeephaven_list_tables called with server_url: {server_url!r}, port: {port!r}")

# Create a new Deephaven Session
session = Session(host=server_url, port=port)
logging.info(f"Session created successfully for host: {server_url}")

# Retrieve the list of available tables
# Note: session.tables is a mapping of table names to Table objects
#       We list the keys (table names) for display
#       If using pydeephaven >=0.26, session.tables is a Mapping[str, Table]
tables = list(session.tables)
logging.info(f"Retrieved tables from session: {tables!r}")

# Close the session to free resources
session.close()
logging.info(f"Session closed for host: {server_url}")
logging.info(f"pydeephaven_list_tables returning tables: {tables!r}")

# Print the list of table names to stdout
print(tables)
