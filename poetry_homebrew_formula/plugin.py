from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cleo.helpers import option
from cleo.io.outputs.output import Verbosity
from jinja2 import Environment, FileSystemLoader
from poetry.console.commands.group_command import GroupCommand
from poetry.plugins import ApplicationPlugin
from poetry.puzzle.solver import Solver
from poetry.repositories.lockfile_repository import LockfileRepository

from poetry_homebrew_formula.types import PackageInfo, RootPackageInfo

if TYPE_CHECKING:
    from poetry.console.application import Application
    from poetry.core.packages.package import Package
    from poetry.core.packages.project_package import ProjectPackage
    from poetry.core.packages.utils.link import Link
    from poetry.repositories.repository import Repository

COMMAND_NAME = "homebrew-formula"
DEFAULT_TEMPLATE = "formula.rb.j2"

HERE = Path(__file__).parent
DEFAULT_TEMPLATE_DIR = HERE / "templates"
TEMPLATE_ENV = Environment(loader=FileSystemLoader([DEFAULT_TEMPLATE_DIR, Path.cwd()]), trim_blocks=True)


class PoetryHomebrewFormulaCommand(GroupCommand):
    name = COMMAND_NAME
    description = "Generate a Homebrew formula for the current project."
    options = [
        *GroupCommand._group_dependency_options(),
        option(
            "template",
            "t",
            "A custom template to render the formula from.",
            flag=False,
        ),
        option(
            "output",
            "o",
            "The name of the formula file to write to.",
            flag=False,
        ),
    ]

    repo: Repository

    def handle(self) -> int:
        self.line("Generating formula ...")
        self.repo = self.poetry.pool.repository("pypi")
        package = self.project_with_activated_groups_only()
        output = Path(self.option("output") or (Path.cwd() / f"{package.name}.rb"))
        self.render_formula(package, output=output)
        return 0

    def render_formula(self, package: ProjectPackage, *, output: Path) -> None:
        template_name = self.option("template") or DEFAULT_TEMPLATE
        template = TEMPLATE_ENV.get_template(template_name)
        self.line(f"Rendering template {template.filename} to {output}", verbosity=Verbosity.VERBOSE)
        formula = template.render(
            package=self.get_root_package_info(package),
            resources=[self.get_package_info(dependency) for dependency in self.resolve_dependencies(package).packages],
            formula_name=package.name.title().replace("-", "").replace("_", ""),
        )

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(formula)

    def resolve_dependencies(self, package: ProjectPackage) -> LockfileRepository:
        locked_repository = self.poetry.locker.locked_repository()
        packages = locked_repository.packages
        solver = Solver(package, self.poetry.pool, packages, packages, self.io)
        ops = solver.solve().calculate_operations(with_uninstalls=False)
        repo = LockfileRepository()
        for op in ops:
            if not repo.has_package(op.package):
                repo.add_package(op.package)

        return repo

    def get_package_info(self, package: Package) -> PackageInfo:
        link = self.pick_link(package)
        return PackageInfo(
            name=package.name,
            url=link.url_without_fragment,
            checksum=link.hash,
            checksum_name=link.hash_name,
        )

    def get_root_package_info(self, package: Package) -> RootPackageInfo:
        link = self.pick_link(package)
        return RootPackageInfo(
            name=package.name,
            license=package.license.id if package.license else None,
            description=package.description,
            homepage=package.homepage or package.repository_url,
            url=link.url_without_fragment,
            checksum=link.hash,
            checksum_name=link.hash_name,
        )

    def pick_link(self, package: Package) -> Link:
        for link in self.repo.find_links_for_package(package):
            if link.is_sdist:
                return link
        raise RuntimeError(f"No valid link found for {package.name}. ")


def factory() -> PoetryHomebrewFormulaCommand:
    return PoetryHomebrewFormulaCommand()


class PoetryHomebrewFormulaPlugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        application.command_loader.register_factory(COMMAND_NAME, factory)
