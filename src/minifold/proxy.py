#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .log import Log
from .singleton import Singleton

try:
    import requests
except ImportError as e:
    Log.warning(
        "Please install requests.\n"
        "  APT: sudo apt install python3-requests\n"
        "  PIP: sudo pip3 install --upgrade requests\n"
    )
    raise e


class Proxy(dict, metaclass=Singleton):
    """
    The :py:class:`Proxy` class is a singleton dictionary storing
    proxy settings.
    It typically maps each protocol (e.g., "http", "https") with
    the corresponding proxy URL (e.g., "http://localhost:8080").

    >>> proxy = Proxy()
    >>> proxy_enable("localhost", 8080)
    >>> proxy_disable()
    """
    pass


def proxy_enable(host: str, port: int, protocols: list = None):
    """
    Enables the :py:class:`Proxy` singleton.

    Args:
        host (str): The proxy FQDN or IP address.
        port (int): The proxy port.
        protocols (list): The list of protocols supported by the proxy.
            Passing ``None`` is equivalent to passing ``["http", "https"]``.
            Defaults to ``None``.
    """
    if not protocols:
        protocols = ["http", "https"]
    proxy = Proxy()
    for protocol in protocols:
        url = f"{protocol}://{host}:{port}"
        proxy[protocol] = url


def proxy_disable():
    """
    Disables the :py:class:`Proxy` singleton.
    """
    proxy = Proxy()
    proxy.clear()


def make_session() -> requests.Session:
    """
    Creates a :py:class:`requests.Session` instance according to
    the :py:class:`Proxy` singleton.

    Returns:
        The corresponding :py:class:`requests.Session` instance.
    """
    session = requests.Session()
    proxy = Proxy()
    if proxy:
        Log.info("Setting proxy = %s" % proxy)
        session.proxies.update(proxy)
    return session


# ---------------------------------------------------------------
# Example to use a local proxy
# ---------------------------------------------------------------

PROXY_LOCALHOST_IP = "127.0.0.1"
PROXY_LOCALHOST_PORT = 8080


def proxy_enable_localhost():
    """
    Illustrative function enabling a local proxy (127.0.0.1:8080).
    """
    proxy_enable(PROXY_LOCALHOST_IP, PROXY_LOCALHOST_PORT)
