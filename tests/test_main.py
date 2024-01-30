from pathlib import Path

import pytest
from cleo.testers.command_tester import CommandTester

from tests.helpers import PoetryTestApplication, TestRepository


def test_init(homebrew_fresh_tap: Path) -> None:
    assert homebrew_fresh_tap.exists()
    assert (homebrew_fresh_tap / "Formula").is_dir()


def test_happy_path_no_args(
    homebrew_fresh_tap_cd: Path, command_tester: CommandTester, app: PoetryTestApplication
) -> None:
    app.poetry.pool.add_repository(TestRepository())
    formula = homebrew_fresh_tap_cd / "simple-project.rb"
    assert not formula.is_file()

    command_tester.execute()

    assert formula.is_file()
    content = formula.read_text()
    assert '  url "https://foo.bar/files/simple_project-1.2.3.tar.gz"' in content
    assert '  sha256 "c9cd57a70bcf3fd2ff24693ac37741f85009805c2f74b10502db0461ec7576ae"' in content


def test_no_repo(tmp_path_cd: Path, command_tester: CommandTester) -> None:
    with pytest.raises(RuntimeError, match="No valid link"):
        command_tester.execute()

    assert list(tmp_path_cd.glob("*.rb")) == []
