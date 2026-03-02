"""CLI help text parser — extracts subcommands as MCP ToolDefinitions."""
import re
import subprocess
from dataclasses import dataclass, field


@dataclass
class ToolDefinition:
    name: str                          # e.g. "git_clone"
    description: str                   # human-readable
    command: list[str]                 # e.g. ["git", "clone"]
    parameters: dict[str, str] = field(default_factory=dict)


def run_help(command: list[str]) -> str:
    """Run a command with --help and return stdout+stderr."""
    try:
        result = subprocess.run(
            command + ["--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout + result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def parse_cli_help(tool_name: str, help_text: str) -> list[ToolDefinition]:
    """Parse CLI --help output into ToolDefinitions."""
    tools: list[ToolDefinition] = []

    # Match lines like:   subcommand   Description of subcommand
    pattern = re.compile(r"^\s{2,}([a-z][a-z0-9_-]*)\s{2,}(.+)$", re.MULTILINE)

    for match in pattern.finditer(help_text):
        subcommand = match.group(1).strip()
        description = match.group(2).strip()

        # Skip option flags (lines with --)
        if subcommand.startswith("-"):
            continue

        tools.append(
            ToolDefinition(
                name=f"{tool_name}_{subcommand}".replace("-", "_"),
                description=description,
                command=[tool_name, subcommand],
            )
        )

    return tools


def parse_cli_tool(tool_name: str) -> list[ToolDefinition]:
    """Parse a CLI tool by running its --help."""
    help_text = run_help([tool_name])
    return parse_cli_help(tool_name, help_text)
