from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from gamebench_hub.models import Benchmark


class PresentMonNotFoundError(RuntimeError):
    pass


def find_presentmon(explicit: Path | None = None) -> Path | None:
    if explicit and explicit.is_file():
        return explicit
    configured = os.environ.get("PRESENTMON_PATH")
    if configured and Path(configured).is_file():
        return Path(configured)
    discovered = shutil.which("PresentMon.exe") or shutil.which("PresentMon")
    return Path(discovered) if discovered else None


@dataclass(frozen=True)
class Summary:
    benchmark_id: str
    app_id: int
    captured_at: str
    frames: int
    average_fps: float
    one_percent_low_fps: float
    average_frametime_ms: float
    p99_frametime_ms: float
    raw_csv: str


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    rank = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[rank]


def summarize_csv(csv_path: Path, benchmark: Benchmark) -> Summary:
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"PresentMon produced no frame rows in {csv_path}")
    candidates = ("msBetweenPresents", "CPUFrameTime", "FrameTime", "DisplayedTime")
    column = next((name for name in candidates if name in rows[0]), None)
    if column is None:
        raise ValueError(f"No supported frame-time column in {csv_path}")
    frame_times: list[float] = []
    for row in rows:
        try:
            value = float(row[column])
        except (KeyError, TypeError, ValueError):
            continue
        if value > 0 and math.isfinite(value):
            frame_times.append(value)
    if not frame_times:
        raise ValueError(f"No valid frame times in {csv_path}")
    average_ms = sum(frame_times) / len(frame_times)
    p99_ms = _percentile(frame_times, 0.99)
    return Summary(
        benchmark_id=benchmark.id,
        app_id=benchmark.app_id,
        captured_at=datetime.now(UTC).isoformat(),
        frames=len(frame_times),
        average_fps=round(1000 / average_ms, 2),
        one_percent_low_fps=round(1000 / p99_ms, 2),
        average_frametime_ms=round(average_ms, 3),
        p99_frametime_ms=round(p99_ms, 3),
        raw_csv=str(csv_path),
    )


class PresentMonCollector:
    def __init__(self, executable: Path, results_dir: Path) -> None:
        self.executable = executable
        self.results_dir = results_dir

    def start(
        self, benchmark: Benchmark, duration: int | None = None
    ) -> tuple[subprocess.Popen[bytes], Path]:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = self.results_dir / benchmark.id / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        csv_path = run_dir / "frames.csv"
        command = [
            str(self.executable),
            "--output_file",
            str(csv_path),
            "--v2_metrics",
            "--stop_existing_session",
            "--no_console_stats",
        ]
        for process_name in benchmark.executable_names:
            command.extend(["--process_name", process_name])
        if duration:
            command.extend(["--timed", str(duration), "--terminate_after_timed"])
        else:
            command.append("--terminate_on_proc_exit")
        return subprocess.Popen(command), csv_path

    @staticmethod
    def finish(process: subprocess.Popen[bytes], csv_path: Path, benchmark: Benchmark) -> Summary:
        exit_code = process.wait()
        if exit_code != 0:
            raise RuntimeError(f"PresentMon exited with status {exit_code}")
        summary = summarize_csv(csv_path, benchmark)
        (csv_path.parent / "summary.json").write_text(
            json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8"
        )
        return summary
