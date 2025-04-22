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

### Typical workflow with uv

1. **Install uv** (if not already):
   ```bash
   pip install uv
   # or
   brew install astral-sh/uv/uv
   ```
2. **Initialize your project (optional):**
   ```bash
   uv init
   uv python pin 3.13  # Pin to your Python version
   ```
3. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   # or add new dependencies:
   uv pip install autogen-ext mcp[cli]
   ```
4. **Create a virtual environment (optional, recommended):**
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```
5. **Run your scripts:**
   ```bash
   uv run src/mcp_server.py
   uv run src/mcp_client.py
   ```

- `uv` will use your `.venv` automatically if present. If you have multiple environments, use `--active` to target the currently activated one.
- You can use `uv` and `venv` together or separately.
- `uv` is fully compatible with `requirements.txt` and `pyproject.toml`.

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

1. Edit `~/Library/Application\ Support/Claude/claude_desktop_config.json`:

    - Using `venv`:

    ```
    {
        "mcpServers": {
            "test-dh-mcp": {
                "command": "/Users/chip/dev/test-dh-mcp/venv/bin/python3",
                "args": ["/Users/chip/dev/test-dh-mcp/src/mcp_server.py", "--transport", "stdio"],
            }
        }
    }
    ```

    - Using `uv`:

    ```
    {
        "mcpServers": {
            "test-dh-mcp": {
                "command": "uv",
                "args": ["run", "/Users/chip/dev/test-dh-mcp/src/mcp_server.py", "--transport", "stdio"],
            }
        }
    }
    ```
    
4. Restart Claude Desktop.
5. Debugging logs can be found in `~/Library/Logs/Claude/`


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

