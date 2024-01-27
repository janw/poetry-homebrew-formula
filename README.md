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
![`poetry run poetry homebrew-formula --help --ansi`](.assets/homebrew-formula-help.svg)

## Custom templates

The plugin allows for the use of custom [Jinja-based templates](https://jinja.palletsprojects.com/en/3.1.x/templates/) to be used when rendering the formula. This is particularly useful for software that requires more a elaborate "packaging recipe" than what the [default template](./poetry_homebrew_formula/templates/formula.rb.j2) can offer. In custom templates, some common components are offered as "shortcode" template tags:

* `{{ PACKAGE_URL }}`: will be replaced with the project own source URL and checksum.
* `{{ RESOURCES }}`: will be replaced with the project's dependencies.

With that in mind, the following uses become possible:

### Prepopulated formula

If you want to define the entire formula yourself and populate only the dynamic components via poetry-homebrew-formula, you may use both shortcodes like so:

```jinja
class MySoftwareProject < Formula
  include Language::Python::Virtualenv

  desc "This is a software project that has its formula prepopulated with most details"
  homepage "https://mysoftwareproject.invalid"
  license "MIT

{{ PACKAGE_URL }}

  depends_on "python3"
  depends_on "rust" => >:build

{{ RESOURCES }}

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources

    doing_something_here
    generate_completions_from_executable(bin/"my-software", shells: [:bash, :zsh, :fish], shell_parameter_format: :click)
  end

  test do
    false
  end
end
```

<details>
<summary><b>Rendered example formula</b></summary>

```rb
class MySoftwareProject < Formula
  include Language::Python::Virtualenv

  desc "This is a software project that has its formula prepopulated with most details"
  homepage "https://mysoftwareproject.invalid"
  license "MIT

  url "https://files.pythonhosted.org/packages/cd/28/fa4281532b4eeb28ba5ead093d24d553ee93861df0f743cad37e01ed6bc6/mysoftwareproject-0.1.0a1.tar.gz"
  sha256 "7158b7e86e9b1399a7aae6a169fd8a4716636284b74870a352f268f852098e2c"

  depends_on "python3"
  depends_on "rust" => >:build

  resource "click" do
    url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/aa/3f/56142232152145ecbee663d70a19a45d078180633321efb3847d2562b490/pydantic-2.5.3.tar.gz"
    sha256 "b3ef57c62535b0941697cce638c08900d87fcb67e29cfa99e8a68f747f393f7a"
  end

  resource "pydantic-core" do
    url "https://files.pythonhosted.org/packages/b2/7d/8304d8471cfe4288f95a3065ebda56f9790d087edc356ad5bd83c89e2d79/pydantic_core-2.14.6.tar.gz"
    sha256 "1fd0c1d395372843fba13a51c28e3bb9d59bd7aebfeb17358ffaaa1e4dbbe948"
  end

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources

    doing_something_here
    generate_completions_from_executable(bin/"fancy-software", shells: [:bash, :zsh, :fish], shell_parameter_format: :click)
  end

  test do
    false
  end
end
```

</details>

### Resources only

If you have other plans and only need the resources to be rendered, your template can also look like this:

```jinja
{{ RESOURCES }}
```

This is effectively replicating the behavior of [homebrew-pypi-poet](https://github.com/tdsmith/homebrew-pypi-poet) in that it only emits the dependency resources:

<details>
<summary><b>Rendered example</b></summary>

```rb
resource "click" do
  url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.7.tar.gz"
  sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
end

resource "pydantic" do
  url "https://files.pythonhosted.org/packages/aa/3f/56142232152145ecbee663d70a19a45d078180633321efb3847d2562b490/pydantic-2.5.3.tar.gz"
  sha256 "b3ef57c62535b0941697cce638c08900d87fcb67e29cfa99e8a68f747f393f7a"
end

resource "pydantic-core" do
  url "https://files.pythonhosted.org/packages/b2/7d/8304d8471cfe4288f95a3065ebda56f9790d087edc356ad5bd83c89e2d79/pydantic_core-2.14.6.tar.gz"
  sha256 "1fd0c1d395372843fba13a51c28e3bb9d59bd7aebfeb17358ffaaa1e4dbbe948"
end
```

</details>

### Templates from `stdin`

The plugin supports template definitions via stdin, as well as emitting them to stdout by using `-` as the option argument:

```bash
$ echo '{{RESOURCES}}' | poetry homebrew-formula -t- -o- | tee my-formula.rb

resource "click" do
  url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.7.tar.gz"
  sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
end

resource "pydantic" do
…
```
