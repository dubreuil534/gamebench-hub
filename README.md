# GameBench Hub

GameBench Hub is an early-stage Python CLI for cataloguing, installing, launching, and measuring
**official standalone game benchmarks**. It delegates downloads to the publisher's official source
(Steam in the first release), so the repository never contains or redistributes game assets.

The initial catalog contains:

| ID | Benchmark | Steam AppID | PresentMon process |
|---|---|---:|---|
| `black-myth-wukong` | Black Myth: Wukong Benchmark Tool | `3132990` | `b1_benchmark.exe`, renderer child |
| `the-alters` | The Alters Benchmark Tool | `3787490` | `TheAlters.exe`, renderer child |
| `bright-memory-infinite-rt` | Bright Memory: Infinite Ray Tracing Benchmark | `1409670` | `BMIBenchMark-Win64-Shipping.exe` |
| `resident-evil-6` | Resident Evil 6 Benchmark Tool | `229950` | `RE6.exe` (`BH6.exe` legacy alias) |

The Steam store listings and current public depot metadata were checked on 2026-09-16. All four
are Windows tools separate from their parent games. The manifests remain ordinary YAML so changes
to AppIDs, process names, and future sources can be reviewed without changing the core CLI.

## What works

- `list`: catalog plus local Steam installation state
- `doctor`: Steam and PresentMon discovery
- `install ID`: opens the official Steam install flow
- `run ID`: launches through Steam and captures with PresentMon when available
- `run-all`: sequentially launches installed catalog entries
- raw per-frame CSV plus a JSON summary with average FPS, 1% low FPS, average frametime, and p99
  frametime
- multiple Steam libraries via `libraryfolders.vdf`
- replaceable runner boundary for future publisher launchers or direct official downloads

GameBench Hub currently launches the tool, but it does not synthesize clicks inside each benchmark.
Most tools still require the user to choose settings and press their in-app **Benchmark** button.
Use a timed capture if a tool does not exit automatically.

## Requirements

- Windows 10 or 11 for the catalogued benchmarks
- Python 3.11+
- Steam desktop client
- optional: the current 64-bit `PresentMon` console executable from Intel's official
  [PresentMon releases](https://github.com/GameTechDev/PresentMon/releases)

PresentMon relies on Windows ETW and may request administrator access. Its upstream documentation
also notes accuracy limitations for some GPU metrics when Hardware-Accelerated GPU Scheduling is
enabled. GameBench Hub calculates its FPS summary from the available per-frame timing column; the
raw CSV is retained for independent analysis.

## Install for development

```powershell
git clone https://github.com/OWNER/gamebench-hub.git
cd gamebench-hub
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

Point the CLI at PresentMon either with an environment variable:

```powershell
$env:PRESENTMON_PATH = "C:\Tools\PresentMon\PresentMon-2.3.1-x64.exe"
```

or per run:

```powershell
gamebench run black-myth-wukong --presentmon C:\Tools\PresentMon\PresentMon.exe
```

## Examples

```text
gamebench list
gamebench doctor
gamebench install black-myth-wukong
gamebench run black-myth-wukong
gamebench run the-alters --duration 180
gamebench run resident-evil-6 --no-collect
gamebench run-all --duration 180 --results-dir results
```

Results are written under:

```text
results/<benchmark-id>/<YYYYMMDD-HHMMSS>/
├── frames.csv
└── summary.json
```

`--duration` starts capture immediately and ends it after the requested number of seconds. Without
it, PresentMon uses `--terminate_on_proc_exit`. Close the benchmark normally after its run so the
summary can be written.

## Architecture

```text
YAML manifests -> Catalog -> BenchmarkService -> Runner (Steam today)
                                      |
                                      +-> PresentMonCollector -> CSV -> JSON summary
```

- `src/gamebench_hub/manifests/`: reviewable benchmark metadata
- `catalog.py` / `models.py`: manifest loading and validation
- `runners.py`: protocol implemented by source-specific runners
- `steam.py`: client discovery, library discovery, install and launch URI handling
- `presentmon.py`: process capture and summary calculation
- `service.py`: orchestration independent from the CLI
- `cli.py`: Typer commands only

See [docs/adding-a-benchmark.md](docs/adding-a-benchmark.md) for the manifest contract.

## Legal and safety

GameBench Hub is not affiliated with Valve, Intel, Game Science, 11 bit studios, FYQD-Studio,
PLAYISM, or Capcom. Names and trademarks belong to their respective owners.

The project stores metadata and invokes official distribution clients. It must not host, mirror,
unpack, patch, bypass DRM for, or redistribute benchmark/game files. Users remain responsible for
the Steam Subscriber Agreement and any publisher EULA shown by Steam.

## Roadmap

- verify capture behavior on Windows hardware for all four initial tools
- tool-specific presets and optional UI automation where publisher terms permit it
- richer run metadata (GPU, driver, resolution, quality preset)
- schema version validation and third-party catalog overlays
- official non-Steam runners

Contributions are welcome under the [MIT License](LICENSE).
