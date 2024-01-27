# poetry-homebrew-formula — Poetry Plugin for Homebrew Formulae

<!-- markdownlint-disable MD033 MD013 -->
<div align="center">

[![version](https://img.shields.io/pypi/v/poetry-homebrew-formula.svg)](https://pypi.org/project/poetry-homebrew-formula/)
[![python](https://img.shields.io/pypi/pyversions/poetry-homebrew-formula.svg)](https://pypi.org/project/poetry-homebrew-formula/)
[![downloads](https://img.shields.io/pypi/dm/poetry-homebrew-formula)](https://pypi.org/project/poetry-homebrew-formula/)

[![Tests](https://github.com/janw/poetry-homebrew-formula/actions/workflows/tests.yaml/badge.svg)](https://github.com/janw/poetry-homebrew-formula/actions/workflows/tests.yaml?query=branch%3Amain)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/janw/poetry-homebrew-formula/main.svg)](https://results.pre-commit.ci/latest/github/janw/poetry-homebrew-formula/main)

[![Maintainability](https://api.codeclimate.com/v1/badges/4ad2ba1c95736b1a66c9/maintainability)](https://codeclimate.com/github/janw/poetry-homebrew-formula/maintainability)
[![codecov](https://codecov.io/gh/janw/poetry-homebrew-formula/graph/badge.svg?token=vS7RKkMkQo)](https://codecov.io/gh/janw/poetry-homebrew-formula)

[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/docs/)
[![pre-commit](https://img.shields.io/badge/-pre--commit-f8b424?logo=pre-commit&labelColor=grey)](https://github.com/pre-commit/pre-commit)

</div>

A plugin for [Poetry](https://python-poetry.org) that renders the dependencies of a given python project into a [Homebrew](https://docs.brew.sh) formula.

This project was inspired by [poetry-brew](https://pypi.org/project/poetry-brew/) that aims to solve the same problem but with a different approach.

## Setup

* If you installed poetry via [pipx](https://pipx.pypa.io/stable/) (preferred):

    ```bash
    pipx inject poetry poetry-homebrew-formula
    ```

* If you installed poetry a different way, most likely this will work, too:

    ```bash
    poetry self add poetry-homebrew-formula
    ```

    Please consult the [poetry docs on using plugins](https://python-poetry.org/docs/plugins/#using-plugins) for more details.

## Usage

Run `poetry homebrew-formula --help` for details on how to use it:

<!-- RICH-CODEX fake_command: "poetry homebrew-formula --help" -->
![`poetry run poetry homebrew-formula --help`](.assets/homebrew-formula-help.svg)
