import json
import logging
import os
from typing import Any

from mcp_x.parsers.cli import ToolDefinition

logger = logging.getLogger(__name__)


def is_enhancement_available() -> bool:
    """Check if Claude API key is available for schema enhancement."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def enhance_tools(
    tools: list[ToolDefinition],
    client: Any = None,
) -> list[ToolDefinition]:
    """Use Claude to improve tool schemas. Falls back to originals on error."""
    if not tools:
        return tools

    if client is None:
        try:
            import anthropic

            client = anthropic.Anthropic()
        except Exception:
            return tools

    tool_list = [
        {"name": t.name, "description": t.description, "command": t.command}
        for t in tools
    ]

    prompt = f"""You are helping generate MCP (Model Context Protocol) tool schemas.

Given these raw tool definitions extracted from a CLI's --help output:
{json.dumps(tool_list, indent=2)}

Return a JSON array with improved schemas. For each tool:
- Write a clear, specific description (1-2 sentences)
- Add a "parameters" object with parameter names as keys and their descriptions as values
- Keep the same "name" field

Return ONLY valid JSON array, no markdown, no explanation."""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
        enhanced = json.loads(raw)

        result = []
        for original, improved in zip(tools, enhanced):
            result.append(
                ToolDefinition(
                    name=improved.get("name", original.name),
                    description=improved.get("description", original.description),
                    command=original.command,
                    parameters=improved.get("parameters", {}),
                )
            )
        return result
    except Exception as e:
        logger.warning(f"LLM enhancement failed, using raw schemas: {e}")
        return tools
