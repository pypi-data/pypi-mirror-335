<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/figs/Veles-logo-white.svg">
    <source media="(prefers-color-scheme: light)" srcset="/figs/Veles-logo.svg">
    <img alt="Veles logo, text Veles with Veles' rune instead of V." src="Veles-logo.svg" width=60%>
  </picture>
</p>
<br>

<!-- badges: start -->

[![PyPI](https://img.shields.io/pypi/v/velesresearch)](https://pypi.org/project/velesresearch/)
[![GitHub](https://img.shields.io/badge/license-GPL--3.0-informational)](https://github.com/jakub-jedrusiak/VelesResearch/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/jakub-jedrusiak/VelesResearch/branch/main/graph/badge.svg?token=CGc3zeDxFi)](https://codecov.io/gh/jakub-jedrusiak/VelesResearch)

<!-- badges: end -->

Veles is a free and open source Python research package, primarly for social scientists. It's goal is to provide an interface for surveys and chronometric experiments. It combines the power of Survey.js and PsychoJS (PsychoPy) with Python interface to create self contained research units that can be self-hosted. Veles' own web service for creating and hosting experiments are planned.

Veles is in pre-alpha development, but the goal features are:

- Free and open source.

- Text-based, so automatable and easily modifiable.

- Ability to use JavaScript and CSS directly.

- [Open source documentation](https://docs.velesweb.org/).

- reCAPTCHA v3 protection from bots by default.

- Detection of pasted answers and writing speed calculation (detect GPT).

- Integration with GitHub.

- Python-based.

- Esay to collaborate through git.

- Custom redirection in the end (for panels).

- PsychoPy integration.

- Modifiable themes.

# Installation

You can install the current version of Veles with:

``` bash
pip install velesresearch
```

You can install development version (unstable) with:

``` bash
pip install velesresearch@git+https://github.com/jakub-jedrusiak/VelesResearch.git
```

Note that **`bun` is required** for Veles to work. Use one of the following commands to install it:

``` bash
# Linux and MacOS
curl -fsSL https://bun.sh/install | bash

# Windows
powershell -c "irm bun.sh/install.ps1|iex"
```

If everything went well, command `bun --version` should return a version number. See [Getting started](getting-started.qmd) if you get any errors.
