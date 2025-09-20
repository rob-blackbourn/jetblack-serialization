# Contributing

## Create the environment

I use standard python environments which I install in the root folder of the
project. I typically call the folder `.venv`, and this is in the `.gitignore`.

```bash
~/jetblack-serialization$ python3.12 -m venv .venv
~/jetblack-serialization$ . .venv/bin/activate
(.venv) ~/jetblack-serialization$
```

## Install the packages

The project uses standard tooling and setuptools.

The project and required packages can be installed with the following command.

```bash
(.venv) ~/jetblack-serialization$ pip install setuptools
(.venv) ~/jetblack-serialization$ pip install -e '.[dev,docs,examples]'
```

## Check types

The python code is typed. Types can be checked by running the standalone
`mypy` command.

```bash
(.venv) ~/jetblack-serialization$ mypy
Success: no issues found in 58 source files
```

## Linting

The project uses pylint.

```bash
(.venv) ~/jetblack-serialization$ pylint jetblack-serialization
```

## Run the tests

The tests can be run as follows.

```bash
(.venv) ~/jetblack-serialization$ pytest tests
```

## Build and publish the package

The following commands build the package and publish it. Note that publishing
requires authentication.

```bash
(.venv) ~/jetblack-serialization$ python -m build
Building jetblack-serialization (4.0.1)
  - Building sdist
  - Built jetblack-serialization-4.0.1.tar.gz
  - Building wheel
  - Built jetblack-serialization-4.0.1-py3-none-any.whl
(.venv) ~/jetblack-serialization$ twine upload dist/*

Username:
```

## Build and push the documentation

The project uses [mkdocs](https://www.mkdocs.org/) to build the docs
and [mike](https://github.com/jimporter/mike) to handle multiple versions. The
docs are served by [GitHub Pages](https://pages.github.com/) on the `gh-pages`
branch.

The following would build and publish version `4.0` and update the `latest`
alias to point to `4.0`.

```
mike deploy --push --update-aliases 4.0 latest
```

Two aliases are configured: `latest` and `stable`. The following would set the
default to `latest`.

```bash
mike set-default --push latest
```