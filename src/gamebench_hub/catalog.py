from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import yaml

from gamebench_hub.models import Benchmark, ManifestError


def default_manifest_dir() -> Path:
    return Path(str(files("gamebench_hub").joinpath("manifests")))


class Catalog:
    def __init__(self, manifest_dir: Path | None = None) -> None:
        self.manifest_dir = manifest_dir or default_manifest_dir()

    def all(self) -> list[Benchmark]:
        benchmarks: list[Benchmark] = []
        for path in sorted(self.manifest_dir.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ManifestError(f"Manifest {path} must contain a YAML mapping")
            benchmarks.append(Benchmark.from_mapping(raw, path))
        return benchmarks

    def get(self, benchmark_id: str) -> Benchmark:
        for benchmark in self.all():
            if benchmark.id == benchmark_id:
                return benchmark
        choices = ", ".join(item.id for item in self.all())
        raise KeyError(f"Unknown benchmark '{benchmark_id}'. Available: {choices}")
