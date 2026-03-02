import socket
from mcp_x.server import find_free_port, build_mcp_app
from mcp_x.parsers.cli import ToolDefinition


def test_find_free_port_returns_int():
    port = find_free_port()
    assert isinstance(port, int)
    assert 1024 < port < 65535


def test_find_free_port_is_available():
    port = find_free_port()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", port))  # should not raise


def test_build_mcp_app_returns_app():
    tools = [
        ToolDefinition(
            name="git_clone",
            description="Clone a repository",
            command=["git", "clone"],
            parameters={"url": "Repository URL"},
        )
    ]
    app = build_mcp_app("git", tools)
    assert app is not None
    assert app.name == "mcp-x-git"
