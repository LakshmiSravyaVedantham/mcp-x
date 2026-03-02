import json
from pathlib import Path


DEFAULT_CONFIG = Path.home() / ".claude.json"
PREFIX = "mcp-x-"


def _load(config_path: Path) -> dict:
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}


def _save(data: dict, config_path: Path) -> None:
    config_path.write_text(json.dumps(data, indent=2))


def register_server(
    name: str,
    port: int,
    config_path: Path = DEFAULT_CONFIG,
) -> None:
    """Register an mcp-x server in Claude's config."""
    data = _load(config_path)
    data.setdefault("mcpServers", {})
    data["mcpServers"][f"{PREFIX}{name}"] = {
        "url": f"http://localhost:{port}",
        "type": "sse",
    }
    _save(data, config_path)


def unregister_server(
    name: str,
    config_path: Path = DEFAULT_CONFIG,
) -> None:
    """Remove an mcp-x server from Claude's config."""
    data = _load(config_path)
    data.setdefault("mcpServers", {})
    data["mcpServers"].pop(f"{PREFIX}{name}", None)
    _save(data, config_path)


def list_servers(config_path: Path = DEFAULT_CONFIG) -> dict[str, str]:
    """List all mcp-x registered servers. Returns {name: url}."""
    data = _load(config_path)
    servers = data.get("mcpServers", {})
    return {
        k[len(PREFIX):]: v["url"]
        for k, v in servers.items()
        if k.startswith(PREFIX)
    }
