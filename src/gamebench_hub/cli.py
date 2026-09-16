from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from gamebench_hub.catalog import Catalog
from gamebench_hub.presentmon import find_presentmon
from gamebench_hub.service import BenchmarkService
from gamebench_hub.steam import SteamRunner, find_steam_root, is_installed

app = typer.Typer(no_args_is_help=True, help="Manage official standalone game benchmarks.")


def _service(results_dir: Path = Path("results")) -> BenchmarkService:
    return BenchmarkService(SteamRunner(), results_dir)


@app.command("list")
def list_benchmarks() -> None:
    """List benchmarks in the bundled catalog."""
    steam_root = find_steam_root()
    typer.echo(f"{'ID':<24} {'APPID':<10} {'INSTALLED':<10} NAME")
    for benchmark in Catalog().all():
        installed = "yes" if is_installed(benchmark.app_id, steam_root) else "no"
        typer.echo(f"{benchmark.id:<24} {benchmark.app_id:<10} {installed:<10} {benchmark.name}")


@app.command()
def doctor() -> None:
    """Check Steam and PresentMon discovery."""
    steam = find_steam_root()
    presentmon = find_presentmon()
    typer.echo(f"Steam: {steam or 'not found'}")
    typer.echo(f"PresentMon: {presentmon or 'not found (optional; set PRESENTMON_PATH)'}")


@app.command()
def install(benchmark_id: Annotated[str, typer.Argument(help="Catalog benchmark id")]) -> None:
    """Ask the official Steam client to install a benchmark."""
    benchmark = Catalog().get(benchmark_id)
    _service().install(benchmark)
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
    if collect and not find_presentmon(presentmon):
        typer.echo("PresentMon not found; launching without capture.", err=True)
    summary = _service(results_dir).run(benchmark, collect, presentmon, duration)
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
    installed = [item for item in catalog if is_installed(item.app_id)]
    if not installed:
        raise typer.BadParameter("No catalog benchmarks are installed in a detected Steam library.")
    service = _service(results_dir)
    for benchmark in installed:
        typer.echo(f"Starting {benchmark.name}...")
        summary = service.run(benchmark, collect, presentmon, duration)
        if summary:
            typer.echo(f"  {summary.average_fps} avg FPS; {summary.one_percent_low_fps} 1% low")
