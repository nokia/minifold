# Package installation (`poetry` + `pip3`)
## Introduction

This section presents two ways to (re)install the package.

* _As a normal user:_ this is the clean approach. But as the runnables are deployed in `~/.local/bin`, you have to update your `PATH` environment variable. To do so, you should to update your `PATH` by adding in the end of your `~/.bashrc` file the following statement, and then restart `bash`:

```bash
export PATH=${PATH}:${HOME}/.local/bin
```

* _As root:_ as the runnables in `/usr/local/bin`, you don't have to update your variable environment variable.

## Full installation

The first time you install the package, just run one of the following commands.

* As a normal user:

```bash
poetry build
pip3 install dist/*whl
```

* As root:

```bash
poetry build
sudo pip3 install dist/*whl
```

## Full reinstallation

As the package is already install, `pip3` may decide to not redeploy the package. Just use the `--force-reinstall` option. Note that `pip3` will check the package dependencies. This is slow, but required if you have modified the dependencies (in `pyproject.toml`).

* As a normal user:
```bash
poetry build
pip3 install dist/*whl --force-reinstall
```
* As root:
```bash
poetry build
sudo pip3 install dist/*whl --break-system-packages --force-reinstall
```

## Fast reinstallation

Most of time, the dependencies are already deployed and you just want to redeploy the package without checking anything. To do so, use the `--no-deps` option as follows.

* As a normal user:
```bash
poetry build
pip3 install dist/*whl --force-reinstall --no-deps
```
* As root:
```bash
poetry build
sudo pip3 install dist/*whl --break-system-packages --force-reinstall --no-deps
```

## Extra dependencies

As explained in [the documentation of Poetry](https://python-poetry.org/docs/pyproject/#extras), an extra is a set of optional dependencies.
* The dependencies specified for each extra must already be defined as project dependencies. 
* Dependencies listed in dependency groups cannot be specified as extras.

The eventual extra(s) proposed by a `.whl` file can be listed by running:

```bash
pkginfo -f provides_extras dist/*whl
```

The dependencies assigned to an extra are:

* defined in the `pyproject.toml` file (see the `[tool.poetry.extras]` block);
* _not_ installed by running a default PIP install, e.g.:

```bash
pip3 install dist/minifold-x.y.z-py3-none-any.whl
```

* are only installed if explicitly this extra is explicitly mentionned, e.g.:

```bash
pip3 install dist/minifold-x.y.z-py3-none-any.whl[extra1] 
```

__Remarks:__  In `poetry`, groups and extras are two distinct notions:

* groups are only related to `poetry install`;
* extras are only related to `pip3 install package[extra1,extra2,...]`.
