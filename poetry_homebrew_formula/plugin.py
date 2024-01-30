from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from cleo.helpers import option
from cleo.io.outputs.output import Verbosity
from poetry.console.commands.group_command import GroupCommand
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry.plugins import ApplicationPlugin
from poetry.puzzle.solver import Solver
from poetry.repositories.lockfile_repository import LockfileRepository

from poetry_homebrew_formula.templating import generate_template, get_template
from poetry_homebrew_formula.types import PackageInfo, RootPackageInfo

if TYPE_CHECKING:
    from jinja2 import Template
    from poetry.console.application import Application
    from poetry.core.packages.package import Package
    from poetry.core.packages.project_package import ProjectPackage
    from poetry.core.packages.utils.link import Link
    from poetry.repositories.repository import Repository

COMMAND_NAME = "homebrew-formula"
RESOURCES_TEMPLATE = "resources.rb.j2"
PACKAGE_URL_TEMPLATE = "package_url.rb.j2"

HERE = Path(__file__).parent


class PoetryHomebrewFormulaCommand(GroupCommand):
    name = COMMAND_NAME
    description = "Generate a Homebrew formula for the current project."
    options = [
        *GroupCommand._group_dependency_options(),
        option(
            "template",
            "t",
            "A custom template to render the formula from. Use '-' to read from stdin.",
            flag=False,
        ),
        option(
            "output",
            "o",
            "The name of the formula file to write to. Use '-' to write to stdout.",
            flag=False,
        ),
    ]

    repo: Repository
    default_groups: set[str] = {MAIN_GROUP}

    def handle(self) -> int:
        if self.option("output") == "-":
            # Poetry/Cleo is entirely oblivious about the concept of emitting anything
            # to stdout. When the user requested that we have to redirect all emitted
            # log output to stderr using this hack:
            self.io._output = self.io._error_output

        self.line_error("<info>Generating formula</info>")
        template = self.load_template()
        package = self.project_with_activated_groups_only()
        package_info = self.get_root_package_info(package)
        resources = [self.get_package_info(dependency) for dependency in self.resolve_dependencies(package).packages]

        self.render_formula(
            template=template,
            package=package_info,
            resources=resources,
            formula_name=package.name.title().replace("-", "").replace("_", ""),
        )
        return 0

    def load_template(self) -> Template:
        if (template := self.option("template")) == "-":
            self.line("Reading template from stdin", verbosity=Verbosity.VERBOSE)

            stdin = sys.stdin.read()
            self.line(f"Template content: {stdin}", verbosity=Verbosity.VERY_VERBOSE)
            return generate_template(stdin)
        return get_template(template)

    def render_formula(
        self,
        *,
        template: Template,
        package: RootPackageInfo,
        resources: list[PackageInfo],
        formula_name: str,
    ) -> None:
        formula = (
            template.render(
                package=package,
                formula_name=formula_name,
                RESOURCES=self._render_resources(resources),
                PACKAGE_URL=self._render_package_url(package),
            ).rstrip()
            + "\n"
        )

        if (output := self.option("output")) == "-":
            self.line("Writing template to stdout", verbosity=Verbosity.VERBOSE)
            sys.stdout.write(formula)
            return
        if not output:
            output = f"{package.name}.rb"

        output_path = Path(output)
        self.line(f"Writing template to {output_path}", verbosity=Verbosity.VERBOSE)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formula)

    def _render_resources(self, resources: list[PackageInfo]) -> str:
        template = get_template(RESOURCES_TEMPLATE)
        return template.render(resources=resources)

    def _render_package_url(self, package: RootPackageInfo) -> str:
        template = get_template(PACKAGE_URL_TEMPLATE)
        return template.render(package=package)

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
        for repo in self.poetry.pool.repositories:
            for link in repo.find_links_for_package(package):
                if link.is_sdist:
                    return link
        raise RuntimeError(f"No valid link found for {package.name}. ")


def factory() -> PoetryHomebrewFormulaCommand:
    return PoetryHomebrewFormulaCommand()


class PoetryHomebrewFormulaPlugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        application.command_loader.register_factory(COMMAND_NAME, factory)
