# test-dh-mcp

This project demonstrates how to define and run an MCP (Multi-Channel Protocol) server using the FastMCP implementation. It includes examples for tool registration, server/client usage, and integration with Claude Desktop and MCP Inspector.

- [MCP Server Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [mcp Python package documentation (PyPI)](https://pypi.org/project/mcp/)


## Project Structure

- `src/mcp_server.py` — Main entrypoint to run the MCP server (configurable for SSE or stdio transport).
- `src/dhmcp/__init__.py` — All tools are registered here using the `@mcp_server.tool()` decorator.
- `src/mcp_client.py` — Example async client for testing tools.
- `requirements.txt` — Python dependencies (including `mcp[cli]` and `autogen-ext`).

## Using `uv` for Dependency Management

[`uv`](https://github.com/astral-sh/uv) is a modern, ultra-fast Python package manager and runner. It can be used as a drop-in replacement for pip and venv, providing faster installs and improved dependency management.

### Key Concepts
- **`pyproject.toml`**: The modern, recommended way to specify your project's dependencies and metadata. uv uses this as the source of truth.
- **`requirements.txt`**: Supported for compatibility with traditional Python tools and workflows. Optional if you use `pyproject.toml`.
- **`uv.lock`**: Lockfile for reproducible installs (auto-managed by uv).

### Modern Workflow (Recommended)
1. **Add dependencies directly to your project:**
   ```bash
   uv pip install <package>
   # Example:
   uv pip install autogen-ext mcp[cli]
   ```
   This updates `pyproject.toml` and `uv.lock`.
2. **Sync environment:**
   ```bash
   uv pip install  # Installs all dependencies from pyproject.toml
   ```
3. **Run scripts:**
   ```bash
   uv run src/mcp_server.py
   uv run src/mcp_client.py
   ```

### Compatibility Workflow (requirements.txt)
- If you have an existing `requirements.txt`, you can use:
  ```bash
  uv pip install -r requirements.txt
  # or
  uv add --requirements requirements.txt
  ```
- This will sync dependencies and update your lockfile. You can keep both files in sync for maximum compatibility.

### Notes
- `requirements.txt` is **optional** with uv. For new projects, you can rely entirely on `pyproject.toml` and `uv.lock`.
- For legacy projects or sharing with users of pip, keep `requirements.txt` up to date.
- `uv` works with or without a virtual environment. Use `uv venv .venv` to create one if desired.
- If you have multiple environments, use `--active` to target the currently activated one.

## Quick Start: Server

### 1. Install dependencies

It is recommended to use a virtual environment:

- Using `venv`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Using `uv`:

```bash
uv pip install -r requirements.txt
```

### 2. Run the MCP Server

From the project root, run (choose the transport that fits your use case):

- **SSE transport (default, for browser/web clients):**
  ```bash
  python src/mcp_server.py
  # or, explicitly:
  python src/mcp_server.py --transport sse
  # or, using uv:
  uv run src/mcp_server.py
  ```
  The server will listen on http://localhost:8000/sse

- **Stdio transport (recommended for Claude Desktop/Inspector):**
  ```bash
  python src/mcp_server.py --transport stdio
  # or, using uv:
  uv run src/mcp_server.py --transport stdio
  ```
  The server will communicate via stdio (no HTTP port needed).

You should see log output indicating the server is running with the selected transport.

## Quick Start: Client

> **Note:** The Python client (`mcp_client.py`) requires the MCP server to be running in **SSE mode** (the default). It will not work if the server is running in stdio mode.

### 1. Install dependencies

It is recommended to use a virtual environment:

- Using `venv`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Using `uv`:

```bash
uv pip install -r requirements.txt
```

### 2. Run the MCP Client

From the project root, run:

- Using `venv`:

```bash
cd src
python -m mcp_client
```

- Using `uv`:

```bash
cd src
uv run mcp_client.py
```

You should see log output indicating the client is running and listing available tools.

## Claude Desktop

You can connect Claude Desktop to your local stdio MCP server to use custom tools.

1. Edit `~/Library/Application\ Support/Claude/claude_desktop_config.json` to add your MCP server. To configure the Deephaven connection for all tools, set the required `DH_MCP_*` environment variables in the `env` key. Example:

    - Using `venv` (with environment variables):

    ```json
    {
      "mcpServers": {
        "test-dh-mcp": {
          "command": "/Users/chip/dev/test-dh-mcp/.venv/bin/python3",
          "args": ["/Users/chip/dev/test-dh-mcp/src/mcp_server.py", "--transport", "stdio"],
          "env": {
            "DH_MCP_HOST": "localhost",
            "DH_MCP_PORT": "10000",
            "DH_MCP_AUTH_TYPE": "Anonymous"
          }
        }
      }
    }
    ```

    - Using `uv` (with environment variables):

    ```json
    {
      "mcpServers": {
        "test-dh-mcp": {
          "command": "uv",
          "args": [
            "--directory",
            "/Users/chip/dev/test-dh-mcp/src",
            "run", 
            "mcp_server.py", 
            "--transport", 
            "stdio"
          ],
          "env": {
            "DH_MCP_HOST": "localhost",
            "DH_MCP_PORT": "10000",
            "DH_MCP_AUTH_TYPE": "Anonymous"
          }
        }
      }
    }
    ```

> **Note:** All `DH_MCP_*` environment variables listed in the Deephaven Session Configuration section can be set here. These control the Deephaven session for every tool call.
    
4. Restart Claude Desktop.
5. Debugging logs can be found in `~/Library/Logs/Claude/`


## Deephaven Session Configuration

All Deephaven session configuration is now handled via environment variables. Tool functions no longer accept `server_url` or `port` arguments. Instead, set the following environment variables to control session behavior:

- `DH_MCP_HOST`: Hostname or IP address of the Deephaven server (default: None)
- `DH_MCP_PORT`: Port number for the Deephaven server (default: None)
- `DH_MCP_AUTH_TYPE`: Authentication type (default: 'Anonymous')
- `DH_MCP_AUTH_TOKEN`: Authentication token (default: '')
- `DH_MCP_NEVER_TIMEOUT`: Whether the session should never timeout (default: True)
- `DH_MCP_SESSION_TYPE`: Session type, e.g., 'python' (default: 'python')
- `DH_MCP_USE_TLS`: Whether to use TLS/SSL (default: False)
- `DH_MCP_TLS_ROOT_CERTS`: Path to TLS root certificates (default: None)
- `DH_MCP_CLIENT_CERT_CHAIN`: Path to client certificate chain (default: None)
- `DH_MCP_CLIENT_PRIVATE_KEY`: Path to client private key (default: None)
- `DH_MCP_CLIENT_OPTS`: Additional client options (default: None)
- `DH_MCP_EXTRA_HEADERS`: Extra headers to include in the session (default: None)

Example (Unix shell):
```sh
export DH_MCP_HOST=localhost
export DH_MCP_PORT=10000
export DH_MCP_AUTH_TYPE=Anonymous
```

All tools in `dhmcp/__init__.py` will use these environment variables to configure the session.

## Registering Tools

Define new tools in `dhmcp/__init__.py` using the `@mcp_server.tool()` decorator. Example:

```python
@mcp_server.tool()
def echo_tool(message: str) -> str:
    """
    Echo tool that returns the input message prefixed with 'Echo:'.
    """
    return f"Echo: {message}"
```

## Troubleshooting

- Ensure you are running commands from the correct directory (`src` for direct script execution).
- If you change tool definitions, restart the server.
- For connection issues, check that the server is running and listening on the expected address/port (for SSE), or correctly attached via stdio (for Claude/Inspector).

### Is the server running?

- **SSE mode:**
  ```bash
  curl http://localhost:8000/sse
  ```
- **Stdio mode:**
  - Check your Claude/Inspector logs for successful connection and tool listing.

### MCP Inspector

The MCP Inspector is a tool that allows you to inspect the state of an MCP server.

1. Install the MCP Inspector:
    ```bash
    npm install -g @modelcontextprotocol/inspector
    ```

2. Run the MCP Inspector:
    - ** SSE mode: **

        - Using `venv`:

        ```bash
        cd /Users/chip/dev/test-dh-mcp/src
        npx @modelcontextprotocol/inspector \
        /Users/chip/dev/test-dh-mcp/venv/bin/python3 mcp_server.py --transport sse
        ```

        - Using `uv`:

        ```bash
        cd /Users/chip/dev/test-dh-mcp/src
        npx @modelcontextprotocol/inspector \
        uv run mcp_server.py --transport sse
        ```

    - ** Stdio mode: **

        - Using `venv`:

        ```
        cd /Users/chip/dev/test-dh-mcp/src
        npx @modelcontextprotocol/inspector \
        /Users/chip/dev/test-dh-mcp/venv/bin/python3 mcp_server.py --transport stdio
        ```

        - Using `uv`:

        ```bash
        cd /Users/chip/dev/test-dh-mcp/src
        npx @modelcontextprotocol/inspector \
        uv run mcp_server.py --transport stdio
        ```

