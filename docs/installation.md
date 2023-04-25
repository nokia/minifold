# Preliminaries
## Linux (Debian / Ubuntu)

Depending on your preferences, you may install the dependencies through APT, or through PIP. Please see the following steps if you want to use APT dependencies.

* Install `poetry`:

```bash
sudo apt update
sudo apt update python3-poetry python3-trove-classifiers
```

* Install the APT dependencies:

```bash
sudo apt install git python3 python3-pytest
```

* If you are a developer, please also install the following dependencies:

```bash
sudo apt install python3-pip bumpversion python3-coverage python3-pytest python3-pytest-cov python3-pytest-runner python3-sphinx python3-sphinx-rtd-theme
sudo pip3 install sphinx_mdinclude --break-system-packages
```

## Windows

* Install [poetry](https://pypi.org/project/poetry/).
* Install [anaconda](https://www.anaconda.com/products/distribution).
* Install [jupyter](https://jupyter.org/install).
* Install [graphviz](https://jupyter.org/install).

# Installation
## From PIP

There are several possible ways to install the package:

* _In a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/):_ this is the recommended approach.

```bash
python3 -m venv env      # Create your virtual environment
source env/bin/activate  # Activate the "env" virtual environment
which python             # Check you use the venv python interpret (i.e., not /usr/bin/python3)
pip install minifold --force-reinstall
deactivate               # Leave the  "env" virtual environment
```

* _System-wide:_ modern ``pip3`` version prevents to install packages system-wide. You must either use a virtual environment, or either pass the `--break-system-packages` options:

```
sudo pip3 install minifold --break-system-packages
```

## From git

* Clone the repository and install the package:

```bash
git clone https://github.com/nokia/minifold.git
cd minifold
```

* Install the missing dependencies and build the wheel of the project:
```
poetry install  # Install the core dependencies. Pass --with docs,test,dev to get the whole set of dependencies.
poetry build    # Build the wheel (see dist/*whl)
```

* Install the wheel you just built, according to one of the following method, that affects the installation scope:
  * _In the `poetry` environment:_ this imposes to run your python-related commands through `poetry run`.

```bash
poetry run pip3 install dist/*whl
```

  * In a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/): this imposes to run your python-related in the venv.

```bash
python3 -m venv env      # Create your virtual environment
source env/bin/activate  # Activate the "env" virtual environment
which python             # Should be your "env" python interpreter (not /usr/bin/python3)
pip install dist/*whl    # Install your wheel
deactivate               # Leave the  "env" virtual environment
```

  * System-wide (Linux):

```bash
sudo pip3 install dist/*whl --break-system-packages --force-reinstall
```
