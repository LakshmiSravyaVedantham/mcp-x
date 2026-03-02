from mcp_x.parsers.cli import ToolDefinition, parse_cli_help

FAKE_HELP = """
usage: git [-v | --version] [-h | --help] <command> [<args>]

These are common Git commands used in various situations:

start a working area (see also: git help tutorial)
   clone     Clone a repository into a new directory
   init      Create an empty Git repository

work on the current change (see also: git help everyday)
   add       Add file contents to the index
   mv        Move or rename a file

Options:
  -v, --version  Prints the Git suite version
  -h, --help     Prints the synopsis and a list of the commands
"""


def test_parses_tool_names():
    tools = parse_cli_help("git", FAKE_HELP)
    names = [t.name for t in tools]
    assert "git_clone" in names
    assert "git_init" in names
    assert "git_add" in names


def test_parses_descriptions():
    tools = parse_cli_help("git", FAKE_HELP)
    clone = next(t for t in tools if t.name == "git_clone")
    assert "Clone a repository" in clone.description


def test_tool_has_command():
    tools = parse_cli_help("git", FAKE_HELP)
    clone = next(t for t in tools if t.name == "git_clone")
    assert clone.command == ["git", "clone"]


def test_returns_list():
    tools = parse_cli_help("git", FAKE_HELP)
    assert isinstance(tools, list)
    assert len(tools) >= 3
