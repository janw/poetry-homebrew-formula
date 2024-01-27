import subprocess
from pathlib import Path
from shutil import rmtree
from typing import Iterator

import pytest

TESTING_TAP_NAME = "janw/poetry-homebrew-formula--testing"


@pytest.fixture(scope="session")
def homebrew_tapdir() -> Path:
    _repo_path = (
        subprocess.check_output(
            (
                "brew",
                "--repo",
                TESTING_TAP_NAME,
            )
        )
        .decode()
        .strip()
    )
    return Path(_repo_path)


@pytest.fixture()
def homebrew_fresh_tap(homebrew_tapdir: Path) -> Iterator[Path]:
    rmtree(homebrew_tapdir, ignore_errors=True)
    (homebrew_tapdir / "Formula").mkdir(parents=True, exist_ok=True)
    (homebrew_tapdir / "README.md").touch()
    yield homebrew_tapdir
    rmtree(homebrew_tapdir, ignore_errors=True)
