# Preliminaries

Ensure the needed dependencies are installed in `poetry`:

```bash
poetry install --with dev,test
```

# Nokia intranet

If the machine running the code is in the Nokia Intranet/VPN (e.g., `lambdav2.nbl.nsn-rdnet.net`),
it is strongly advised to add the following lines to the end of your ``~/.bashrc``.

```bash
export http_proxy="http://10.158.100.3:8080"
export https_proxy="$http_proxy"
# PIP proxy configuration: pip config set global.proxy $http_proxy
# If pip install -v get stuck, see: https://unix.stackexchange.com/a/635597
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```
