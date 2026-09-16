from pathlib import Path

from gamebench_hub.steam import is_installed, library_roots


def test_detects_appmanifest_in_secondary_library(tmp_path: Path) -> None:
    steam = tmp_path / "Steam"
    library = tmp_path / "Games"
    (steam / "steamapps").mkdir(parents=True)
    (library / "steamapps").mkdir(parents=True)
    (steam / "steamapps" / "libraryfolders.vdf").write_text(
        f'"libraryfolders"\n{{\n  "1" {{ "path" "{library}" }}\n}}', encoding="utf-8"
    )
    (library / "steamapps" / "appmanifest_3132990.acf").touch()
    assert library_roots(steam) == [steam, library]
    assert is_installed(3132990, steam)
