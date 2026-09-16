from gamebench_hub.catalog import Catalog
from gamebench_hub.platforms import is_supported


def test_windows_benchmark_platform_compatibility() -> None:
    benchmark = Catalog().get("black-myth-wukong")
    assert is_supported(benchmark, "windows")
    assert not is_supported(benchmark, "macos")
