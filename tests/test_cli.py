from typer.testing import CliRunner

from gamebench_hub.cli import app

runner = CliRunner()


def test_list_command_shows_catalog() -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Black Myth: Wukong Benchmark Tool" in result.output
    assert "3787490" in result.output
