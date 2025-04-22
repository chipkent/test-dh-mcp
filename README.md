# test-dh-mcp

This project demonstrates how to define and run an MCP (Multi-Channel Protocol) server using the FastMCP implementation.

## Project Structure

- `src/dhmcp/server.py` — Main entrypoint to configure and run the MCP server.
- `src/dhmcp/tools.py` — Example tools registered with the MCP server using decorators.
- `requirements.txt` — Python dependencies (including `mcp[cli]`).

## Quick Start

### Using this server with Claude Desktop

You can connect Claude Desktop to your local MCP server to use custom tools.

1. **Start the MCP server** as described below (see 'Run the MCP Server').
2. **Open Claude Desktop**.
3. Go to **Settings > Integrations > MCP Servers** (or similar, depending on your version).
4. Click **Add MCP Server** and enter the following URL:

   ```
   http://localhost:8000/mcp
   ```

   If you changed the port or host, adjust the URL accordingly (e.g., `http://127.0.0.1:YOUR_PORT/mcp`).

5. Save and enable the integration.
6. Claude Desktop should now be able to discover and use the tools you have registered in your MCP server (e.g., `echo_tool`).

For more details, see the Claude Desktop documentation for MCP integration.


### 1. Install dependencies

It is recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the MCP Server

From the project root, run:

```bash
cd src
python -m dhmcp.server
```

You should see log output indicating the server is running (by default on port 8000, using SSE transport).

### 3. Registering Tools

Define new tools in `tools.py` using the `@mcp_server.tool()` decorator. Example:

```python
@mcp_server.tool()
def echo_tool(message: str) -> str:
    """
    Echo tool that returns the input message prefixed with 'Echo:'.
    """
    return f"Echo: {message}"
```

## Troubleshooting

- Ensure you are running commands from the correct directory (`src` for module execution).
- If you change tool definitions, restart the server.
- For connection issues, check that the server is running and listening on the expected address/port.

---

For more information, see the documentation for the [mcp](https://pypi.org/project/mcp/) package.
