from pathlib import Path

import pytest

from poetry_homebrew_formula.exceptions import GenericTemplateError, TemplateNotFoundError
from poetry_homebrew_formula.templating import DEFAULT_TEMPLATE, generate_template, get_template


def test_default_template() -> None:
    tmpl = get_template()
    assert tmpl
    assert tmpl.name == DEFAULT_TEMPLATE

    tmpl = get_template(None)
    assert tmpl
    assert tmpl.name == DEFAULT_TEMPLATE


def test_not_found() -> None:
    with pytest.raises(TemplateNotFoundError):
        get_template("/nonexistent")


def test_invalid(tmp_path_cd: Path) -> None:
    template_path = tmp_path_cd / "invalid.j2"
    template_path.write_text("{{notclosed}")
    with pytest.raises(GenericTemplateError):
        get_template(str(template_path))


def test_relative_absolute(tmp_path_cd: Path) -> None:
    template_path = tmp_path_cd / "valid.j2"
    template_path.write_text("{{unused}}")

    tmpl = get_template(template_path)
    assert tmpl
    assert tmpl.name
    assert tmpl.name.startswith("/")
    assert tmpl.name.endswith("valid.j2")

    tmpl = get_template("valid.j2")
    assert tmpl
    assert tmpl.name == "valid.j2"


def test_generate_template() -> None:
    tmpl = generate_template("{{unused}}")
    assert tmpl
    assert not tmpl.name
    assert "memory:" in repr(tmpl)


def test_generate_template_empty() -> None:
    with pytest.raises(GenericTemplateError):
        generate_template("  ")


def test_generate_template_invalid() -> None:
    with pytest.raises(GenericTemplateError):
        generate_template("{{notclosed}")
