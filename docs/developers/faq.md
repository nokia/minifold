# FAQ

## `pip` errors

__Q:__ `pip` can't install anything

If the machine running the code is in the Nokia Intranet/VPN (e.g., `lambdav2.nbl.nsn-rdnet.net`),
it is strongly advised to add the following lines to the end of your `~/.bashrc`.
```bash
export http_proxy="http://10.158.100.3:8080"
export https_proxy="$http_proxy"
```
Restart your shell, and run:
```bash
pip config set global.proxy $http_proxy 
```

__Q:__ `pip install -v ...` hangs

This problem is reported [in this thread](https://unix.stackexchange.com/questions/634262/pip-hangs-on-loading-macos-when-installing-a-package/635597#635597).
To fix it, add the following lines to the end of your `~/.bashrc`.
```bash
# If pip install -v freezes, see: https://unix.stackexchange.com/a/635597
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```

## `poetry` errors

__Q:__ `poetry install` hangs

Check whether you can install the impacted dependencies using `pip install -v ...`.
If this command also hangs, see the corresponding item in this FAQ.

__Q:__ `poetry install` is very slow (e.g., in the CI)

It occurs if some dependencies must be recompiled.
This is especially a problem for large package (like `numpy`).
It is advised to constrain `pyproject.toml` so that the package only rely on binaries well.

__Example:__

```toml
[tool.poetry.dependencies
numpy = [
    {version = ">=1.26.1", python = ">=3.9"},
    {version = "*", python = "<3.9"}
]
```

## CUDA

__Q:__ I get `CUDA error: CUBLAS_STATUS_NOT_INITIALIZED`

This error is reported in [pytorch forum](https://discuss.pytorch.org/t/cuda-error-cublas-status-not-initialized-when-calling-cublascreate-handle/125450).
It occurs when no GPU is available.
In practice, this is often because the GPU that you are about to use is already in use.
If your machine has several GPUs, you could probably just use another one.

* You can monitor which GPU are in use thanks to:
```bash
nvidia-smi
```

* To run `my_command` on GPU 1, run:
```bash
CUDA_VISIBLE_DEVICES=1 my_command
```
