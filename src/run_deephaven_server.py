"""
run_deephaven_server.py
----------------------
This script launches a Deephaven server using the deephaven-server Python package, with configurable JVM arguments for memory and authentication.

Features:
- Starts the server on a user-specified host and port (defaults: localhost:10000)
- Allocates 8GB RAM to the JVM
- Disables authentication using AnonymousAuthenticationHandler
- Creates example tables (t1, t2, t3) for demonstration or testing
- Keeps the server running until interrupted (Ctrl+C)

Usage:
    uv run ./src/run_deephaven_server.py [--host HOST] [--port PORT]

Arguments:
    --host HOST   Hostname or IP address to bind the server (default: localhost)
    --port PORT   Port number for the Deephaven server (default: 10000)

Requirements:
    - deephaven-server Python package installed
    - Java available in PATH
    - Sufficient memory for JVM

Environment:
    - host: Hostname or IP address to bind the server (overridden by --host)
    - port: Port number for the Deephaven server (overridden by --port)
    - jvm_args: JVM arguments for memory and authentication configuration
"""

from deephaven_server import Server
import time

import argparse

# Parse command-line arguments for host and port
parser = argparse.ArgumentParser(description="Launch a Deephaven server with configurable host and port.")
parser.add_argument('--host', type=str, default='localhost', help='Hostname or IP address to bind the server (default: localhost)')
parser.add_argument('--port', type=int, default=10000, help='Port number for the Deephaven server (default: 10000)')
args = parser.parse_args()

host = args.host
port = args.port

# Set JVM args for 8GB RAM and disable authentication
jvm_args = [
    "-Xmx8g",  # Allocate 8GB heap memory
    "-DAuthHandlers=io.deephaven.auth.AnonymousAuthenticationHandler"  # Disable authentication
]

print(f"Starting Deephaven server on {host}:{port} with 8GB RAM and no authentication ...")

# Initialize and start the Deephaven server
server = Server(
    host=host,
    port=port,
    jvm_args=jvm_args,
)
server.start()

# Create example tables for demonstration
from deephaven import empty_table, time_table

t1 = empty_table(1000000).update(["C1 = i", "C2 = ii", "C3 = `abc`"])
t2 = t1.update(["C4 = C1 + 1000000"])
t3 = time_table("PT15m").update(["C1 = i", "C2 = ii", "C3 = `abc`"])

if port != 10000:
    t4 = empty_table(1000000).update(["C1 = i", "C2 = ii", "C3 = `abc`"])

# Keep the server running until interrupted by user
print("Press Ctrl+C to exit")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting Deephaven...")
    server.stop()
