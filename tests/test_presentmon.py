from pathlib import Path

from gamebench_hub.catalog import Catalog
from gamebench_hub.presentmon import summarize_csv


def test_summarize_presentmon_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "frames.csv"
    csv_path.write_text(
        "Application,CPUFrameTime\nbench.exe,10\nbench.exe,20\nbench.exe,30\n",
        encoding="utf-8",
    )
    benchmark = Catalog().get("black-myth-wukong")
    summary = summarize_csv(csv_path, benchmark)
    assert summary.frames == 3
    assert summary.average_fps == 50.0
    assert summary.one_percent_low_fps == 33.33
