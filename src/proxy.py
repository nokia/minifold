#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob, Fabien Mathieu"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com, fabien.mathieu@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

import requests
from .log       import Log
from .singleton import Singleton

class Proxy(dict, metaclass=Singleton):
    pass

def proxy_enable(host :str, port :int, protocols :list = ["http", "https"]):
    proxy = Proxy()
    for protocol in protocols:
        url = "%s://%s:%s" % (protocol, host, port)
        proxy[protocol] = url

def proxy_disable():
    proxy = Proxy()
    proxy.clear()

def make_session() -> requests.Session:
    session = requests.Session()
    proxy = Proxy()
    if proxy:
        Log.info("Setting proxy = %s" % proxy)
        session.proxies.update(proxy)
    return session

#---------------------------------------------------------------
# Example to use a local proxy
#---------------------------------------------------------------

PROXY_LOCALHOST_IP    = "127.0.0.1"
PROXY_LOCALHOST_PORT  = 8080

def proxy_enable_localhost():
    proxy_enable(PROXY_LOCALHOST_IP, PROXY_LOCALHOST_PORT)
