# Tests suite (`pytest`)

## Adding tests

* By convention, the test suite (`tests/`) should follow the same organization as the sources (`src/minifold`).
* Each file is prefixed by `test_`. For example, `src/minifold/my_class.py` corresponds to `tests/test_my_class.py`).
* Inside the test file, each test function must be prefixed by `test_` and an arbitrary suffix, usually the name of the tested function/method.
  * A test succeed if no `Exception` (including `AssertionError`) is raised.
  * Example:

```python
#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from minifold import MyClass


def test_my_class():
	my_class = MyClass()
	# ...
```

## Running tests

To launch the whole test suite, run:

```bash
poetry run pytest
```

You could also run a specific test:

```bash
poetry run pytest tests/test_my_class.py
```
