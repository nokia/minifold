#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

import os, sys
from minifold.cache         import DEFAULT_CACHE_STORAGE_BASE_DIR, DEFAULT_CACHE_STORAGE_LIFETIME
from minifold.filesystem    import check_writable_directory, mkdir

try:
    import requests_cache
except ImportError as e:
    print(
        "Please install requests-cache.\n" + \
        "  APT: sudo apt install python3-requests-cache\n" + \
        "  PIP: sudo pip3 install --upgrade requests-cache\n",
        file = sys.stderr
    )
    raise e

def install_cache(cache_filename :str = None):
    if not cache_filename:
        directory = DEFAULT_CACHE_STORAGE_BASE_DIR
        cache_filename = os.path.join(DEFAULT_CACHE_STORAGE_BASE_DIR, "requests_cache")
    else:
        directory = os.path.dirname(cache_filename)
    mkdir(directory)
    check_writable_directory(directory)
    requests_cache.install_cache(
        cache_filename,
        expire_after = DEFAULT_CACHE_STORAGE_LIFETIME
    )
