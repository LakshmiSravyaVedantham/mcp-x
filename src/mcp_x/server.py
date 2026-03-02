"""MCP server builder for mcp-x.

Converts a list of ToolDefinition objects into a running MCP Server that
Claude can connect to via the Model Context Protocol.
"""

import socket
import subprocess
from typing import Any

import mcp.types as types
from mcp.server import Server

from mcp_x.parsers.cli import ToolDefinition


def find_free_port() -> int:
    """Bind to port 0 to let the OS assign a free port, then return it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def build_mcp_app(tool_name: str, tools: list[ToolDefinition]) -> Server:
    """Create an MCP Server named ``mcp-x-{tool_name}`` with handlers for
    the given list of ToolDefinition objects.

    Args:
        tool_name: Short name identifying the toolset (e.g. ``"git"``).
        tools: ToolDefinition objects describing the available tools.

    Returns:
        A configured :class:`mcp.server.Server` instance.
    """
    app: Server[None, Any] = Server(f"mcp-x-{tool_name}")

    # Build a lookup map for fast dispatch in call_tool
    tool_map: dict[str, ToolDefinition] = {t.name: t for t in tools}

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        result: list[types.Tool] = []
        for td in tools:
            properties: dict[str, Any] = {
                param: {"type": "string", "description": desc}
                for param, desc in td.parameters.items()
            }
            schema: dict[str, Any] = {
                "type": "object",
                "properties": properties,
                "required": list(td.parameters.keys()),
            }
            result.append(
                types.Tool(
                    name=td.name,
                    description=td.description,
                    inputSchema=schema,
                )
            )
        return result

    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        if name not in tool_map:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: unknown tool '{name}'",
                )
            ]

        td = tool_map[name]
        cmd = list(td.command) + [str(v) for v in arguments.values()]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = proc.stdout + proc.stderr
        except FileNotFoundError as exc:
            output = f"Error: command not found — {exc}"
        except subprocess.TimeoutExpired:
            output = "Error: command timed out after 60 seconds"

        return [types.TextContent(type="text", text=output)]

    return app
