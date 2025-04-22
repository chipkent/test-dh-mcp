"""
mcp_client.py

Async Python client for discovering and calling tools on an MCP (Model Context Protocol) server using SSE.

- Connects to a running MCP server via SSE endpoint and lists available tools.
- Optionally demonstrates how to ping the server or call a specific tool.
- Requires `autogen-ext[mcp]` to be installed.

Edit the `url` and `headers` parameters as needed for your server configuration.

Example:
    $ PYTHONPATH=./src python src/mcp_client.py

See the project README for further details.
"""

import asyncio
from autogen_core import CancellationToken
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools

async def main():
    """
    Connects to the MCP server, lists available tools, and demonstrates basic tool invocation.

    - Establishes a connection to the MCP server using SSE.
    - Lists all registered tools on the server.
    - Optionally pings the server or calls a sample tool (see commented code).
    - Modify the tool names and arguments as needed for your server setup.
    """
    # Set up server params for your MCP SSE server
    server_params = SseServerParams(
        url="http://localhost:8000/sse",  # Adjust endpoint as needed
        headers={"Authorization": "Bearer YOUR_TOKEN"}  # Optional
    )

    # Get all available tools (this also establishes the connection)
    tools = await mcp_server_tools(server_params)

    # Ping (if supported as a tool)
    ping_tool = next((t for t in tools if t.name == "ping"), None)
    if ping_tool:
        result = await ping_tool.call({})
        print("Ping result:", result)

    # List tools
    print("Available tools:", [t.name for t in tools])

    # Call a tool (example: 'echo_tool')
    echo_tool = next((t for t in tools if t.name == "echo_tool"), None)
    if echo_tool:
        result = await echo_tool.run_json({"message": "Hello, world!"}, cancellation_token=CancellationToken())
        print("echo_tool result:", result)

    # Call a tool (example: 'gnome_count_colorado')
    gnome_count_tool = next((t for t in tools if t.name == "gnome_count_colorado"), None)
    if gnome_count_tool:
        result = await gnome_count_tool.run_json({}, cancellation_token=CancellationToken())
        print("gnome_count_colorado result:", result)

if __name__ == "__main__":
    asyncio.run(main())
