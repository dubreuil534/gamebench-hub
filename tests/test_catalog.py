from pathlib import Path

import pytest

from gamebench_hub.catalog import Catalog
from gamebench_hub.models import ManifestError


def test_bundled_catalog_has_verified_app_ids() -> None:
    app_ids = {item.id: item.app_id for item in Catalog().all()}
    assert app_ids == {
        "black-myth-wukong": 3132990,
        "bright-memory-infinite-rt": 1409670,
        "resident-evil-6": 229950,
        "the-alters": 3787490,
    }


def test_invalid_manifest_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "broken.yaml").write_text("name: Missing fields\n", encoding="utf-8")
    with pytest.raises(ManifestError):
        Catalog(tmp_path).all()
