from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from poetry.console.application import Application
from poetry.core.packages.package import Package
from poetry.core.packages.utils.link import Link
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories import Repository
from poetry.repositories.exceptions import PackageNotFound
from poetry.utils._compat import metadata

if TYPE_CHECKING:
    from poetry.core.packages.dependency import Dependency
    from poetry.plugins import ApplicationPlugin


class BaseTestRepository(Repository):
    def __init__(self, name: str = "foo", *args: Any, **kwargs: Any) -> None:
        super().__init__(name, *args, **kwargs)

    def find_packages(self, dependency: Dependency) -> list[Package]:
        packages = super().find_packages(dependency)
        if len(packages) == 0:
            raise PackageNotFound(f"Package [{dependency.name}] not found.")

        return packages

    def gen_url(self, package: Package) -> str:
        raise NotImplementedError

    def find_links_for_package(self, package: Package) -> list[Link]:
        return [Link(self.gen_url(package=package))]


class TestRepositoryNoHash(BaseTestRepository):
    def gen_url(self, package: Package) -> str:
        name = package.name.replace("-", "_")
        vers = package.version.to_string()
        return f"https://foo.bar/files/{name}-{vers}.tar.gz"


class TestRepository(TestRepositoryNoHash):
    def gen_url(self, package: Package) -> str:
        sha256 = "#sha256=c9cd57a70bcf3fd2ff24693ac37741f85009805c2f74b10502db0461ec7576ae"
        return super().gen_url(package) + sha256


class TestRepositoryNoSdist(TestRepositoryNoHash):
    def gen_url(self, package: Package) -> str:
        return super().gen_url(package)[:-6] + ".whl"


class PoetryTestApplication(Application):
    def __init__(self, poetry: Poetry) -> None:
        super().__init__()
        self._poetry = poetry

    def reset_poetry(self) -> None:
        assert self._poetry is not None
        poetry = self._poetry
        self._poetry = Factory().create_poetry(self._poetry.file.path.parent)
        self._poetry.set_pool(poetry.pool)
        self._poetry.set_config(poetry.config)


def make_entry_point_from_plugin(
    name: str, cls: type[ApplicationPlugin], dist: metadata.Distribution | None = None
) -> metadata.EntryPoint:
    group: str | None = getattr(cls, "group", None)
    ep = metadata.EntryPoint(
        name=name,
        group=group,  # type: ignore[arg-type]
        value=f"{cls.__module__}:{cls.__name__}",
    )

    if dist:
        ep = ep._for(dist)  # type: ignore[attr-defined]
        return ep

    return ep


def mock_metadata_entry_points(
    cls: type[ApplicationPlugin], name: str = "my-plugin", dist: metadata.Distribution | None = None
) -> None:
    patch.object(
        metadata,
        "entry_points",
        return_value=[make_entry_point_from_plugin(name, cls, dist)],
    )
