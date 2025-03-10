# Linter (`flake8`)
## Basic checks

To check the quality of the code, use `flake8`:

```bash
poetry run flake8 src/ tests/
```

## CI checks

The following command reproduce what is done by the continuous integartion (CI) script.
Ensure that the following commands successfully pass before running `git push`.

```bash
# Stops the build if there are Python syntax errors or undefined names
poetry run flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
poetry run flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```
