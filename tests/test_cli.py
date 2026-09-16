from typer.testing import CliRunner

from gamebench_hub.cli import app

runner = CliRunner()


def test_list_command_shows_catalog() -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Black Myth: Wukong Benchmark Tool" in result.output
    assert "3787490" in result.output


def test_doctor_reports_the_platform() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Platform:" in result.output


def test_run_rejects_incompatible_platform(monkeypatch) -> None:
    monkeypatch.setattr("gamebench_hub.platforms.current_platform", lambda: "macos")
    result = runner.invoke(app, ["run", "black-myth-wukong", "--no-collect"])
    assert result.exit_code == 2
    assert "supports Windows, not macOS" in result.output
