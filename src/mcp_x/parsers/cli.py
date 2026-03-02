"""CLI help text parser — extracts subcommands as MCP ToolDefinitions."""
from dataclasses import dataclass, field


@dataclass
class ToolDefinition:
    name: str
    description: str
    command: list[str]
    parameters: dict[str, str] = field(default_factory=dict)


def parse_cli_help(tool_name: str, help_text: str) -> list[ToolDefinition]:
    """Parse CLI help output and return a list of ToolDefinitions.

    Each detected subcommand becomes one ToolDefinition whose command is
    [tool_name, subcommand].
    """
    tools: list[ToolDefinition] = []
    for line in help_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split(None, 1)
        if len(parts) < 2:
            continue
        candidate, description = parts
        # Accept only simple alphanumeric subcommand tokens (no flags, no punctuation)
        if candidate.isalpha() and candidate.islower():
            tools.append(
                ToolDefinition(
                    name=f"{tool_name}_{candidate}",
                    description=description.strip(),
                    command=[tool_name, candidate],
                )
            )
    return tools
