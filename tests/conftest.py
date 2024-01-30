import os
import subprocess
from pathlib import Path
from shutil import rmtree
from typing import Iterator

import pytest
from cleo.testers.command_tester import CommandTester
from poetry.config.config import Config
from poetry.core.packages.project_package import ProjectPackage
from poetry.packages.locker import Locker
from poetry.poetry import Poetry
from responses import RequestsMock

from poetry_homebrew_formula.plugin import COMMAND_NAME
from tests.helpers import PoetryTestApplication, TestRepository

TESTING_TAP_NAME = "janw/poetry-homebrew-formula--testing"

FIXTURES_DIR = Path(__file__).parent / "fixtures"


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


@pytest.fixture()
def tmp_path_cd(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[Path]:
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(request.config.invocation_params.dir)


@pytest.fixture()
def homebrew_fresh_tap_cd(request: pytest.FixtureRequest, homebrew_fresh_tap: Path) -> Iterator[Path]:
    os.chdir(homebrew_fresh_tap)
    yield homebrew_fresh_tap
    os.chdir(request.config.invocation_params.dir)


@pytest.fixture(scope="session")
def poetry_config() -> Config:
    return Config()


@pytest.fixture()
def repo(responses: RequestsMock) -> TestRepository:
    return TestRepository(name="foo")


@pytest.fixture()
def poetry(poetry_config: Config) -> Poetry:
    project_path = FIXTURES_DIR / "simple_project"
    return Poetry(
        project_path / "pyproject.toml",
        {},
        ProjectPackage("simple-project", "1.2.3"),
        Locker(project_path / "poetry.lock", {}),
        poetry_config,
    )


@pytest.fixture()
def app(poetry: Poetry) -> PoetryTestApplication:
    app_ = PoetryTestApplication(poetry)
    app_._load_plugins()
    return app_


@pytest.fixture()
def command_tester(app: PoetryTestApplication) -> CommandTester:
    command_obj = app.find(COMMAND_NAME)
    tester = CommandTester(command_obj)
    app_io = app.create_io()
    formatter = app_io.output.formatter
    tester.io.output.set_formatter(formatter)
    tester.io.error_output.set_formatter(formatter)

    return tester
