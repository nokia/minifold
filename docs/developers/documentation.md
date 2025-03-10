# Documentation (`sphinx`)
## Dependencies

Ensure that all the needed dependencies are intalled in `poetry`:
```bash
poetry install --with docs
```

## With `make`

```bash
poetry run make docs
```

## Without `make`

```bash
poetry run sphinx-apidoc -f -o docs/ src/
poetry run sphinx-build -b html docs/ docs/_build
```
