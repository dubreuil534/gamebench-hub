from __future__ import annotations

from typing import Protocol

from gamebench_hub.models import Benchmark


class Runner(Protocol):
    """Installation/launch boundary for Steam and future official sources."""

    def install(self, benchmark: Benchmark) -> None: ...

    def run(self, benchmark: Benchmark) -> None: ...
