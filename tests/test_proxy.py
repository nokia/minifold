#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.proxy import Proxy, proxy_enable_localhost, proxy_disable


def test_proxy_disabled():
    proxy = Proxy()
    assert not proxy.get("http")
    assert not proxy.get("https")


def test_proxy_enable_disable():
    proxy = Proxy()
    proxy_enable_localhost()
    assert proxy["http"] == "http://127.0.0.1:8080"
    assert proxy["https"] == "https://127.0.0.1:8080"
    proxy_disable()
    assert not proxy.get("http")
    assert not proxy.get("https")
