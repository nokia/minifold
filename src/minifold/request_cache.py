#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import os, sys
from .cache import DEFAULT_CACHE_STORAGE_BASE_DIR, DEFAULT_CACHE_STORAGE_LIFETIME
from .filesystem import check_writable_directory, mkdir

try:
    import requests_cache
except ImportError as e:
    from .log import Log
    Log.warning(
        "Please install requests-cache.\n"
        "  APT: sudo apt install python3-requests-cache\n"
        "  PIP: sudo pip3 install --upgrade requests-cache\n"
    )
    raise e

def install_cache(cache_filename :str = None):
    """
    Enables ``requests_cache`` for minifold, hence allowing to cache HTTP queries
    issued by minifold.

    Args:
        cache_filename (str): The path to the minifold cache. You may pass
            ``None`` to use the default path (i.e., ``~/.minifold/cache/requests_cache``
            under Linux).
    """
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
