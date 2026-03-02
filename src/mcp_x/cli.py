"""CLI entry point for mcp-x."""

import click

from mcp_x import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """mcp-x: Turn any CLI tool or REST API into an MCP server for Claude."""
