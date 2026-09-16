from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Raised when a benchmark manifest is invalid."""


@dataclass(frozen=True)
class Benchmark:
    id: str
    name: str
    description: str
    platforms: tuple[str, ...]
    source_type: str
    app_id: int
    store_url: str
    executable_names: tuple[str, ...]
    automation: str
    manifest_path: Path

    @classmethod
    def from_mapping(cls, data: dict[str, Any], path: Path) -> Benchmark:
        try:
            source = data["source"]
            launch = data["launch"]
            benchmark = cls(
                id=str(data["id"]),
                name=str(data["name"]),
                description=str(data.get("description", "")),
                platforms=tuple(str(item) for item in data["platforms"]),
                source_type=str(source["type"]),
                app_id=int(source["app_id"]),
                store_url=str(source["store_url"]),
                executable_names=tuple(str(item) for item in launch["executable_names"]),
                automation=str(data.get("automation", "manual_start")),
                manifest_path=path,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ManifestError(f"Invalid manifest {path}: {exc}") from exc
        if benchmark.source_type != "steam":
            raise ManifestError(f"Unsupported source type in {path}: {benchmark.source_type}")
        if not benchmark.id or not benchmark.executable_names:
            raise ManifestError(f"Manifest {path} needs an id and executable_names")
        return benchmark
