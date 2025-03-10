# Tests coverage (`coverage`)

_Note:_ You can safely ignore this section as it is unapplicable. Indeed, due to `opencv`, `coverage run -m pytest` cannot produce a good report and so you cannot compute the coverage

To evaluate the test coverage, run:

```bash
poetry run coverage run -m pytest
poetry run coverage xml
```

* Else, with `tox`:
  * The versions of python that are tested are listed in `tox.ini`.
  * To run the tests, run:

```bash
tox -e py
```


