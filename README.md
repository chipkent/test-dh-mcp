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

1. Edit `~/Library/Application\ Support/Claude/claude_desktop_config.json` to add your MCP server. Deephaven worker configuration is now handled entirely via a JSON config file, and the path must be specified using the required `DH_MCP_CONFIG_FILE` environment variable. There is no default path—this environment variable must always be set.

    Example Claude Desktop config (using venv):

    ```json
    {
      "mcpServers": {
        "test-dh-mcp": {
          "command": "/Users/chip/dev/test-dh-mcp/.venv/bin/python3",
          "args": ["/Users/chip/dev/test-dh-mcp/src/mcp_server.py", "--transport", "stdio"],
          "env": {
            "DH_MCP_CONFIG_FILE": "/Users/chip/dev/test-dh-mcp/deephaven_workers.json"
          }
        }
      }
    }
    ```

    Or with `uv`:

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
            "DH_MCP_CONFIG_FILE": "/Users/chip/dev/test-dh-mcp/deephaven_workers.json"
          }
        }
      }
    }
    ```

    > Note: Always set `DH_MCP_CONFIG_FILE` in the `env` section if your config is not named `deephaven_workers.json` in the project root, or if you want to be explicit about the config location.

          "args": [
            "--directory",
            "/Users/chip/dev/test-dh-mcp/src",
            "run", 
            "mcp_server.py", 
            "--transport", 
            "stdio"
          ],
          "env": {
            "DH_MCP_SERVER_NAME": "test-dh-mcp",
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


## Deephaven Worker Configuration

All Deephaven worker configuration is now handled via a JSON file. The path to this file must be specified using the `DH_MCP_CONFIG_FILE` environment variable. There is no default path—this variable is required.

The config file should look like this:

```json
{
  "workers": {
    "worker1": {
      "host": "localhost",
      "port": 10000,
      "auth_type": "Anonymous",
      "auth_token": "",
      "never_timeout": true
    },
    "worker2": {
      "host": "otherhost",
      "port": 10001,
      "auth_type": "Bearer",
      "auth_token": "YOUR_TOKEN"
    }
  },
  "default_worker": "worker1"
}
```

- The `workers` object maps worker names to their connection settings.
- The `default_worker` is optional and used if a worker name is not specified in a tool call. If set, it must match one of the keys in the `workers` dictionary.

> **Important:** The `DH_MCP_CONFIG_FILE` environment variable must always be set to the path of your worker config file. There is no default config path.

**Supported fields for each worker:**

| Field               | Type           | Description                                                                 |
|---------------------|----------------|-----------------------------------------------------------------------------|
| `host`              | `str`          | Deephaven server hostname or IP (optional)                                  |
| `port`              | `int`          | Deephaven server port (optional)                                            |
| `auth_type`         | `str`          | Authentication type (e.g., `Anonymous`, `Bearer`) (optional)                |
| `auth_token`        | `str`          | Authentication token (optional)                                             |
| `never_timeout`     | `bool`         | Whether the session should never timeout (optional, default: True)          |
| `session_type`      | `str`          | Session type, e.g., `python` (optional, default: 'python')                  |
| `use_tls`           | `bool`         | Whether to use TLS/SSL (optional, default: False)                           |
| `tls_root_certs`    | `str` or `null`| Path to TLS root certificates (optional)                                    |
| `client_cert_chain` | `str` or `null`| Path to client certificate chain (optional)                                 |
| `client_private_key`| `str` or `null`| Path to client private key (optional)                                       |

> Note: You may define workers with only a subset of these fields, depending on your use case and authentication method. No fields are strictly required; defaults will be used where possible.

### Tool Usage

- `echo_tool(message: str) -> str`: Echoes back the input message, prefixed with 'Echo:'.
- `gnome_count_colorado() -> int`: Returns the current number of gnomes in Colorado (demo tool).
- `deephaven_worker_names() -> list[str]`: Returns all configured Deephaven worker names from the config file.
- `deephaven_default_worker() -> str`: Returns the name of the default worker as set in config (or None if not set).
- `deephaven_list_tables(worker_name: str = None) -> list`: Lists table names for the specified worker. If `worker_name` is not provided, uses the default_worker from config.
- `deephaven_table_schemas(worker_name: str = None) -> list`: Returns schemas for all tables in the specified worker. If `worker_name` is not provided, uses the default_worker from config.

See the example config file above for how to set up multiple workers.

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

