"""CLI entry point for mcp-x."""

import json
import logging
import sys

import click

from mcp_x import __version__
from mcp_x.config import list_servers, register_server, unregister_server
from mcp_x.detector import InputType, detect_input_type
from mcp_x.enhancer import enhance_tools, is_enhancement_available
from mcp_x.loader import load_openapi_spec
from mcp_x.parsers.cli import parse_cli_tool
from mcp_x.parsers.openapi import parse_openapi_spec

logging.basicConfig(level=logging.WARNING)


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """mcp-x — Turn any CLI tool or REST API into an MCP server for Claude."""


@main.command()
@click.argument("target")
@click.option("--port", default=0, help="Port to run on (default: auto)")
@click.option("--no-llm", is_flag=True, help="Skip Claude schema enhancement")
@click.option(
    "--eject", is_flag=True, help="Print generated schemas instead of running server"
)
def run(target: str, port: int, no_llm: bool, eject: bool) -> None:
    """Turn TARGET (CLI tool or OpenAPI URL/file) into an MCP server."""
    try:
        input_type = detect_input_type(target)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Detected: {input_type.value} — {target}")

    if input_type == InputType.CLI:
        click.echo(f"Parsing {target} --help ...")
        tools = parse_cli_tool(target)
    else:
        click.echo(f"Loading OpenAPI spec from {target} ...")
        spec = load_openapi_spec(target)
        tools = parse_openapi_spec(spec)

    if not tools:
        click.echo("No tools found. Check the target is correct.", err=True)
        sys.exit(1)

    click.echo(f"Found {len(tools)} tools.")

    if not no_llm and is_enhancement_available():
        click.echo("Enhancing schemas with Claude (use --no-llm to skip) ...")
        tools = enhance_tools(tools)
    elif not no_llm and not is_enhancement_available():
        click.echo("Tip: Set ANTHROPIC_API_KEY for smarter schemas.")

    if eject:
        data = [
            {
                "name": t.name,
                "description": t.description,
                "command": t.command,
                "parameters": t.parameters,
            }
            for t in tools
        ]
        click.echo(json.dumps(data, indent=2))
        return

    # Start server (import here so server.py not required for eject/list modes)
    from mcp_x.server import build_mcp_app, find_free_port

    actual_port = port if port else find_free_port()
    tool_name = target.split("/")[-1].split(".")[0]
    app = build_mcp_app(tool_name, tools)

    register_server(tool_name, actual_port)
    click.echo(
        f"\n{tool_name} ({len(tools)} tools) available to Claude on :{actual_port}"
    )
    click.echo("Auto-registered in ~/.claude.json")
    click.echo("Press Ctrl+C to stop.\n")

    try:
        import uvicorn
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):  # type: ignore[no-untyped-def]
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(routes=[Route("/sse", endpoint=handle_sse)])
        uvicorn.run(
            starlette_app, host="localhost", port=actual_port, log_level="warning"
        )
    except KeyboardInterrupt:
        pass
    finally:
        unregister_server(tool_name)
        click.echo(f"\nStopped. Removed {tool_name} from ~/.claude.json")


@main.command(name="list")
def list_cmd() -> None:
    """List all mcp-x servers registered with Claude."""
    servers = list_servers()
    if not servers:
        click.echo("No mcp-x servers registered.")
        return
    click.echo("Registered mcp-x servers:")
    for name, url in servers.items():
        click.echo(f"  {name:20s} {url}")


@main.command()
@click.argument("name")
def remove(name: str) -> None:
    """Remove a registered mcp-x server from Claude's config."""
    unregister_server(name)
    click.echo(f"Removed {name} from ~/.claude.json")
