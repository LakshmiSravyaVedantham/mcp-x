from click.testing import CliRunner

from mcp_x.cli import main


def test_help_shows_usage():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "mcp-x" in result.output.lower() or "usage" in result.output.lower()


def test_list_command_with_no_servers():
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert (
        "no" in result.output.lower()
        or "registered" in result.output.lower()
        or result.output.strip() == ""
    )


def test_run_requires_target():
    runner = CliRunner()
    result = runner.invoke(main, ["run"])
    assert result.exit_code != 0


def test_run_eject_with_git():
    runner = CliRunner()
    result = runner.invoke(main, ["run", "git", "--eject", "--no-llm"])
    # Should print JSON tool schemas and exit 0
    assert result.exit_code == 0
    assert "[" in result.output  # JSON array output
