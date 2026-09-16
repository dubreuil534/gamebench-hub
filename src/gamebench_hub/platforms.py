from __future__ import annotations

import platform

from gamebench_hub.models import Benchmark

PLATFORM_NAMES = {
    "windows": "Windows",
    "macos": "macOS",
    "linux": "Linux",
}


class UnsupportedPlatformError(RuntimeError):
    """Raised when a benchmark cannot run on the current operating system."""


def current_platform() -> str:
    system = platform.system()
    return {
        "Windows": "windows",
        "Darwin": "macos",
        "Linux": "linux",
    }.get(system, system.lower() or "unknown")


def display_name(platform_id: str) -> str:
    return PLATFORM_NAMES.get(platform_id, platform_id)


def is_supported(benchmark: Benchmark, platform_id: str | None = None) -> bool:
    active_platform = platform_id or current_platform()
    return active_platform in benchmark.platforms


def ensure_supported(benchmark: Benchmark, platform_id: str | None = None) -> None:
    active_platform = platform_id or current_platform()
    if is_supported(benchmark, active_platform):
        return
    supported = ", ".join(display_name(item) for item in benchmark.platforms)
    raise UnsupportedPlatformError(
        f"{benchmark.name} supports {supported}, not {display_name(active_platform)}."
    )
