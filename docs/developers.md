# Developer's corner
## pytest and flake

To launch the test suite, run:

```bash
poetry install --with test
poetry run pytest
```

## Coverage

To evaluate the test coverage, run:

```bash
poetry install --with dev
poetry run coverage run -m pytest
poetry run coverage xml
```

* Else, with `tox`:
  * The versions of python that are tested are listed in `tox.ini`.
  * To run the tests, run:

```bash
tox -e py
```

## Programming style

To check the programming style, run:

```bash
poetry install --with dev
```

To check the quality of the code, use `flake8`:
```bash
# Stops the build if there are Python syntax errors or undefined names
poetry run flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
poetry run flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```
... or directly:
```bash
poetry run flake8 src/ tests/
```

## Documentation

To build the documentation, run:
* If `make` is installed:

```bash
poetry install --with docs
poetry run make docs
```

* Otherwise:

```bash
poetry run sphinx-apidoc -f -o docs/ src/
poetry run sphinx-build -b html docs/ docs/_build
```

## Publish a release
### Initialization

1. Create a token in Pypi.

2. Configure this token in your GitHub repository (in the settings tab)
* `PYPI_USERNAME`: `__token__`
* `PYPI_TOKEN`: `pypi-xxxxxxxxxxxx`

3. Configure this token in poetry so that you can use `poetry publish` in the future
```bash
poetry config pypi-token.pypi pypi-xxxxxxxxxxxx
```

### New release

1. Update the changelog `HISTORY.md`, then add and commit this change:

```bash
git add README.md
git commit -m "Updated README.md"
```

2. Increase the version number using `bumpversion`:

```bash
bumpversion patch # Possible values major / minor / patch
git push
git push --tags
```

3. Optionnally, in GitHub, create a release for the tag you have created.
It publishes the package to PyPI (see `.github/workflows/publish_on_pypi.yml`).
Alternatively, you could run:

```bash
poetry publish
```

## Modifying the project dependencies

Update the `pyproject.toml` file. Then, run:
```bash
poetry lock
poetry install
```
You could check the dependencies of your wheels thanks to `pkginfo`:
```bash
pkginfo -f requires_dist dist/*whl
```
