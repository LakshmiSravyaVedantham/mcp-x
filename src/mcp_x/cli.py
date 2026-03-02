"""CLI entry point for mcp-x."""

import click


@click.group()
@click.version_option()
def main() -> None:
    """mcp-x: Turn any CLI tool or REST API into an MCP server for Claude."""
