from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Annotated, TypeVar

import typer

from gamebench_hub.catalog import Catalog
from gamebench_hub.platforms import (
    UnsupportedPlatformError,
    current_platform,
    display_name,
    ensure_supported,
    is_supported,
)
from gamebench_hub.presentmon import find_presentmon
from gamebench_hub.service import BenchmarkService
from gamebench_hub.steam import SteamRunner, find_steam_root, is_installed

app = typer.Typer(no_args_is_help=True, help="Manage official standalone game benchmarks.")
T = TypeVar("T")


def _service(results_dir: Path = Path("results")) -> BenchmarkService:
    return BenchmarkService(SteamRunner(), results_dir)


def _platform_action(action: Callable[[], T]) -> T:
    try:
        return action()
    except UnsupportedPlatformError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("list")
def list_benchmarks() -> None:
    """List benchmarks in the bundled catalog."""
    steam_root = find_steam_root()
    typer.echo(f"{'ID':<24} {'APPID':<10} {'COMPATIBLE':<12} {'INSTALLED':<10} NAME")
    for benchmark in Catalog().all():
        installed = "yes" if is_installed(benchmark.app_id, steam_root) else "no"
        compatible = "yes" if is_supported(benchmark) else "no"
        typer.echo(
            f"{benchmark.id:<24} {benchmark.app_id:<10} {compatible:<12} "
            f"{installed:<10} {benchmark.name}"
        )


@app.command()
def doctor() -> None:
    """Check Steam and PresentMon discovery."""
    platform_id = current_platform()
    steam = find_steam_root()
    presentmon = find_presentmon()
    compatible = sum(is_supported(item, platform_id) for item in Catalog().all())
    total = len(Catalog().all())
    typer.echo(f"Platform: {display_name(platform_id)}")
    typer.echo(f"Steam: {steam or 'not found'}")
    if platform_id == "windows":
        typer.echo(f"PresentMon: {presentmon or 'not found (optional; set PRESENTMON_PATH)'}")
    else:
        typer.echo("PresentMon: unavailable (Windows ETW only)")
    typer.echo(f"Compatible catalog entries: {compatible}/{total}")


@app.command()
def install(benchmark_id: Annotated[str, typer.Argument(help="Catalog benchmark id")]) -> None:
    """Ask the official Steam client to install a benchmark."""
    benchmark = Catalog().get(benchmark_id)
    _platform_action(lambda: _service().install(benchmark))
    typer.echo(f"Steam installation opened for {benchmark.name} ({benchmark.app_id}).")


@app.command()
def run(
    benchmark_id: Annotated[str, typer.Argument(help="Catalog benchmark id")],
    collect: Annotated[bool, typer.Option("--collect/--no-collect")] = True,
    presentmon: Annotated[Path | None, typer.Option(help="Path to PresentMon executable")] = None,
    duration: Annotated[int | None, typer.Option(min=1, help="Timed capture in seconds")] = None,
    results_dir: Annotated[Path, typer.Option(help="Result storage directory")] = Path("results"),
) -> None:
    """Launch one benchmark and optionally collect PresentMon metrics."""
    benchmark = Catalog().get(benchmark_id)
    _platform_action(lambda: ensure_supported(benchmark))
    if collect and not find_presentmon(presentmon):
        if current_platform() == "windows":
            typer.echo("PresentMon not found; launching without capture.", err=True)
        else:
            typer.echo("PresentMon is Windows-only; launching without capture.", err=True)
    summary = _platform_action(
        lambda: _service(results_dir).run(benchmark, collect, presentmon, duration)
    )
    if summary:
        typer.echo(
            f"{benchmark.name}: {summary.average_fps} avg FPS, "
            f"{summary.one_percent_low_fps} 1% low FPS ({summary.frames} frames)"
        )
    else:
        typer.echo(f"Launched {benchmark.name}. Start its benchmark from the application UI.")


@app.command("run-all")
def run_all(
    collect: Annotated[bool, typer.Option("--collect/--no-collect")] = True,
    presentmon: Annotated[Path | None, typer.Option(help="Path to PresentMon executable")] = None,
    duration: Annotated[
        int | None, typer.Option(min=1, help="Capture seconds per benchmark")
    ] = None,
    results_dir: Annotated[Path, typer.Option(help="Result storage directory")] = Path("results"),
) -> None:
    """Run each installed benchmark sequentially."""
    catalog = Catalog().all()
    compatible = [item for item in catalog if is_supported(item)]
    if not compatible:
        typer.echo(
            f"Error: no catalog benchmarks support {display_name(current_platform())} yet.",
            err=True,
        )
        raise typer.Exit(code=2)
    installed = [item for item in compatible if is_installed(item.app_id)]
    if not installed:
        raise typer.BadParameter("No catalog benchmarks are installed in a detected Steam library.")
    service = _service(results_dir)
    for benchmark in installed:
        typer.echo(f"Starting {benchmark.name}...")
        summary = service.run(benchmark, collect, presentmon, duration)
        if summary:
            typer.echo(f"  {summary.average_fps} avg FPS; {summary.one_percent_low_fps} 1% low")
