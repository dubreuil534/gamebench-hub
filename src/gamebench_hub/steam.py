from __future__ import annotations

import os
import platform
import re
import subprocess
from pathlib import Path

from gamebench_hub.models import Benchmark


class SteamNotFoundError(RuntimeError):
    pass


def _windows_registry_path() -> Path | None:
    if platform.system() != "Windows":
        return None
    try:
        import winreg

        for hive, key_name in (
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        ):
            try:
                with winreg.OpenKey(hive, key_name) as key:
                    value, _ = winreg.QueryValueEx(key, "SteamPath")
                    return Path(value)
            except OSError:
                continue
    except ImportError:
        pass
    return None


def find_steam_root() -> Path | None:
    candidates = [
        _windows_registry_path(),
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Steam",
        Path.home() / ".steam" / "steam",
        Path.home() / ".local" / "share" / "Steam",
        Path.home() / "Library" / "Application Support" / "Steam",
    ]
    for candidate in candidates:
        if candidate and str(candidate) != "." and candidate.exists():
            return candidate
    return None


def library_roots(steam_root: Path) -> list[Path]:
    roots = [steam_root]
    library_file = steam_root / "steamapps" / "libraryfolders.vdf"
    if not library_file.exists():
        return roots
    text = library_file.read_text(encoding="utf-8", errors="ignore")
    for raw_path in re.findall(r'"path"\s+"([^"]+)"', text):
        path = Path(raw_path.replace(r"\\", "\\"))
        if path not in roots:
            roots.append(path)
    return roots


def is_installed(app_id: int, steam_root: Path | None = None) -> bool:
    root = steam_root or find_steam_root()
    if root is None:
        return False
    return any(
        (library / "steamapps" / f"appmanifest_{app_id}.acf").exists()
        for library in library_roots(root)
    )


class SteamRunner:
    def __init__(self, steam_root: Path | None = None) -> None:
        self.steam_root = steam_root or find_steam_root()

    def ensure_available(self) -> None:
        if self.steam_root is None:
            raise SteamNotFoundError(
                "Steam was not detected. Install or start the Steam client first."
            )

    def _open_uri(self, uri: str) -> None:
        self.ensure_available()
        system = platform.system()
        if system == "Windows":
            os.startfile(uri)  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["open", uri])
        else:
            subprocess.Popen(["xdg-open", uri])

    def install(self, benchmark: Benchmark) -> None:
        self._open_uri(f"steam://install/{benchmark.app_id}")

    def run(self, benchmark: Benchmark) -> None:
        self._open_uri(f"steam://run/{benchmark.app_id}")
