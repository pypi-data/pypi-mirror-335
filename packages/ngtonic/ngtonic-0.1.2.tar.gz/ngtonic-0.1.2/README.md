<h1 align="center">ngtonic</h1>
<h3 align="center">Finances in your terminal</h2>

<p align="center">
<img alt="Linux" src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black">
<img alt="Python" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff">
<a href="https://pypi.org/project/ngtonic/">
<img alt="CI" src="https://img.shields.io/pypi/v/ngtonic?logo=pypi&logoColor=white">
</a>
<img alt="PyPI - License" src="https://img.shields.io/pypi/l/ngtonic">


</p>

## Motivation and description




## Should I use this

The things you need before installing the software.

* You need this
* And you need this
* Oh, and don't forget this

## Installation

You can install it with pip but I would recomend using [pipx](https://pipx.pypa.io/stable/installation/) as a better alternative.

```bash
pipx install ngtonic
```

## Development

```bash
pdm install
$(pdm venv activate)
pre-commit install
```

This will create the virtual environment, install the dependencies (including ngtonic itself) and setup some helper commit hooks. Any change on the code will have effect, no need to install it again.

You can also run manually the linter with `pdm lint` or the formatter with `pdm format`.

## Releases

The python packages are uploaded from the CI when creating a release, but you can create an whl locally with `pdm build`.
