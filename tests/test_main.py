from pathlib import Path


def test_init(homebrew_fresh_tap: Path) -> None:
    assert homebrew_fresh_tap.exists()
    assert (homebrew_fresh_tap / "Formula").is_dir()
