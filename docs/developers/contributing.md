# Contributing 

This tutorial explains the steps that you should follow to add a new feature of the package.
The shell commands listed below must be run from the root directory of the `minifold` project (which contains `pyproject.toml`).

## New module
### Naming conventions

* A file/directory is always named in the lower case using underscores as word separator (e.g., `my_class.py`).
* When creating a new file, choose the appropriate directory in  `src/minifold` if any, otherwise, add your file to the top directory.
* Create your module (e.g., `src/minifold/my_class.py`)

### Skeleton

The best is probably to copy/paste the base class, and then update the code of the methods.
Hence, you won't forget to overload some virtual pure methods.
For sake of concision, we define below a boilerplate class. 

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class MyClass:
    pass
```

### Reinstall the package 

Reinstall the `minifold` package and check whether we can import the `MyClass` class.
* Below, we assume we want to deploy the package in the current user's home directory, without checking the dependencies.
* In the documentation, see the installation page for alternative installations.

```sh
poetry build
pip3 install dist/*whl --no-deps --break-system-packages --force-reinstall
```

### Import test

Run a python interpreter, e.g., `python3` or `ipython3` and try to import the `MyClass` class:

```python
import minifold.my_class import MyClass
```

### Import redirection

To make your class available at various package level, expose the `MyClass` in the `__init.py` located in the same directory `my_class.py` and each parent directory.

* `minifold/__init__.py`:

```python
from .my_class import MyClass
```

* `minifold/__init__.py`:

```python
from .my_class import MyClass
```

After reinstalling the package, you could now import the `MyClass` from a python interpreter as follow:

```python
# Absolute import (in any python script)
import minifold.my_class import MyClass
import minifold import MyClass
```

## Guidelines

### Import conventions

* Inside the `minifold` package implementation (in `src/`), you should use relative imports:
```python
# Relative import (only inside the minifold package)
# . : from the same directory
# .. : from the parent directory
# ... : from the grandparent directory, etc.
```

* Otherwise (external scripts, tests suite, etc.), use absolute imports.
* Try to import package in the lexical order for sake of readability.

### Naming conventions

* Conform to PEP8 convention

### Other recommendations

* Always reinstall the package before testing it.
* Check the code quality and fix the eventual errors.
* Please document your code using the [Sphinx Google style](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html).
  * Once the docstrings are added to your code, check whether the documentation still builds, and fix the eventual errors/warnings.
  * Check whether it is correctly rendered in the API section.
* Add tests (e.g., `tests/test_my_class.py` file) if relevant.
  * In practice, classes that require an input video/frame to be tested is not tested, because we don't want to add in the test suite.
  * Once the tests are added, check whether the test suite still passes.

For more details, see the other pages in the developers section.
