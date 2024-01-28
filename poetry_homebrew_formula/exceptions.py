from __future__ import annotations

from poetry.console.exceptions import PoetryConsoleError


class PoetryHomebrewFormulaError(PoetryConsoleError):
    exit_code = 1


class TemplateNotFoundError(PoetryHomebrewFormulaError):
    exit_code = 2


class GenericTemplateError(PoetryHomebrewFormulaError):
    exit_code = 3
