from unittest.mock import MagicMock, patch

from mcp_x.enhancer import enhance_tools, is_enhancement_available
from mcp_x.parsers.cli import ToolDefinition


def test_enhance_returns_same_count():
    tools = [
        ToolDefinition(
            name="git_clone", description="Clone a repo", command=["git", "clone"]
        ),
        ToolDefinition(name="git_add", description="Add files", command=["git", "add"]),
    ]
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [
        MagicMock(
            text='[{"name": "git_clone", "description": "Clone a Git repository into a new directory", "parameters": {"url": "Repository URL to clone", "directory": "Local directory name"}}, {"name": "git_add", "description": "Add file contents to the staging index", "parameters": {"pathspec": "Files to add"}}]'
        )
    ]
    mock_client.messages.create.return_value = mock_message

    result = enhance_tools(tools, client=mock_client)
    assert len(result) == 2


def test_enhance_updates_description():
    tools = [
        ToolDefinition(name="git_clone", description="Clone", command=["git", "clone"]),
    ]
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [
        MagicMock(
            text='[{"name": "git_clone", "description": "Clone a Git repository into a new directory", "parameters": {"url": "Repository URL"}}]'
        )
    ]
    mock_client.messages.create.return_value = mock_message

    result = enhance_tools(tools, client=mock_client)
    assert (
        "directory" in result[0].description.lower()
        or "repository" in result[0].description.lower()
    )


def test_enhance_falls_back_on_error():
    tools = [
        ToolDefinition(name="git_clone", description="Clone", command=["git", "clone"]),
    ]
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API error")

    result = enhance_tools(tools, client=mock_client)
    assert result[0].name == "git_clone"
    assert result[0].description == "Clone"


def test_is_enhancement_available_false_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert is_enhancement_available() is False
