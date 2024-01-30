from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, Template, TemplateError, TemplateNotFound

from poetry_homebrew_formula.exceptions import GenericTemplateError, TemplateNotFoundError

DEFAULT_TEMPLATE = "formula.rb.j2"


class CustomFileSystemLoader(FileSystemLoader):
    def __init__(self, encoding: str = "utf-8") -> None:
        super().__init__([], encoding, False)

    def get_source(self, environment: Environment, template: str) -> tuple[str, str, None]:  # type: ignore[override]
        path = Path(template).resolve()
        if not path.is_file():
            raise TemplateNotFound(template)

        with path.open(encoding=self.encoding) as fp:
            contents = fp.read()

        return contents, str(path), None

    def list_templates(self) -> list[str]:
        return []  # pragma: no cover


TEMPLATE_ENV = Environment(
    loader=ChoiceLoader(
        [
            CustomFileSystemLoader(),
            PackageLoader("poetry_homebrew_formula", "templates"),
        ]
    ),
    trim_blocks=True,
    autoescape=False,
)


def get_template(name: str | Path | None = None) -> Template:
    if isinstance(name, Path):
        name = str(name)
    elif not name:
        name = DEFAULT_TEMPLATE

    try:
        return TEMPLATE_ENV.get_template(name)
    except TemplateNotFound as exc:
        raise TemplateNotFoundError(f"Formula template '{name}' was not found.") from exc
    except TemplateError as exc:
        raise GenericTemplateError(f"Formula template '{name}' is invalid: {exc}.") from exc


def generate_template(content: str) -> Template:
    content = content.rstrip()
    if not content:
        raise GenericTemplateError("Formula template is invalid: cannot be empty.")
    try:
        return TEMPLATE_ENV.from_string(content)
    except TemplateError as exc:
        raise GenericTemplateError(f"Formula template is invalid: {exc}.") from exc
