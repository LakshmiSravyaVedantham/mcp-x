from enum import Enum
import shutil


class InputType(Enum):
    CLI = "cli"
    OPENAPI = "openapi"


def detect_input_type(target: str) -> InputType:
    """Detect whether target is a CLI tool name or OpenAPI spec (URL or file path)."""
    if not target:
        raise ValueError("Cannot determine input type for empty target")

    # URL → OpenAPI
    if target.startswith("http://") or target.startswith("https://"):
        return InputType.OPENAPI

    # File extension → OpenAPI
    if target.endswith((".json", ".yaml", ".yml")):
        return InputType.OPENAPI

    # Exists as a command → CLI
    if shutil.which(target):
        return InputType.CLI

    # Fallback: treat as CLI (user might give full path)
    if "/" in target or target.startswith("."):
        return InputType.CLI

    raise ValueError(f"Cannot determine input type for: {target!r}")
