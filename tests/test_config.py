import json
import tempfile
from pathlib import Path
from mcp_x.config import register_server, unregister_server, list_servers


def test_register_creates_entry(tmp_path):
    config_file = tmp_path / ".claude.json"
    register_server("git", 8742, config_path=config_file)
    data = json.loads(config_file.read_text())
    assert "mcpServers" in data
    assert "mcp-x-git" in data["mcpServers"]


def test_register_sets_url(tmp_path):
    config_file = tmp_path / ".claude.json"
    register_server("git", 8742, config_path=config_file)
    data = json.loads(config_file.read_text())
    assert data["mcpServers"]["mcp-x-git"]["url"] == "http://localhost:8742"


def test_register_preserves_existing(tmp_path):
    config_file = tmp_path / ".claude.json"
    config_file.write_text(json.dumps({"mcpServers": {"existing": {"url": "http://localhost:9000"}}}))
    register_server("git", 8742, config_path=config_file)
    data = json.loads(config_file.read_text())
    assert "existing" in data["mcpServers"]
    assert "mcp-x-git" in data["mcpServers"]


def test_unregister_removes_entry(tmp_path):
    config_file = tmp_path / ".claude.json"
    register_server("git", 8742, config_path=config_file)
    unregister_server("git", config_path=config_file)
    data = json.loads(config_file.read_text())
    assert "mcp-x-git" not in data.get("mcpServers", {})


def test_list_servers_returns_mcp_x_entries(tmp_path):
    config_file = tmp_path / ".claude.json"
    register_server("git", 8742, config_path=config_file)
    register_server("psql", 8743, config_path=config_file)
    servers = list_servers(config_path=config_file)
    assert "git" in servers
    assert "psql" in servers
