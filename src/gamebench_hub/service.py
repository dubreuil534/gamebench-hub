from __future__ import annotations

from pathlib import Path

from gamebench_hub.models import Benchmark
from gamebench_hub.presentmon import PresentMonCollector, Summary, find_presentmon
from gamebench_hub.runners import Runner


class BenchmarkService:
    def __init__(self, runner: Runner, results_dir: Path = Path("results")) -> None:
        self.runner = runner
        self.results_dir = results_dir

    def install(self, benchmark: Benchmark) -> None:
        self.runner.install(benchmark)

    def run(
        self,
        benchmark: Benchmark,
        collect: bool = True,
        presentmon_path: Path | None = None,
        duration: int | None = None,
    ) -> Summary | None:
        executable = find_presentmon(presentmon_path) if collect else None
        if not executable:
            self.runner.run(benchmark)
            return None
        collector = PresentMonCollector(executable, self.results_dir)
        process, csv_path = collector.start(benchmark, duration)
        self.runner.run(benchmark)
        return collector.finish(process, csv_path, benchmark)
