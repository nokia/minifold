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

import datetime, functools, json, os, pickle, sys, traceback

from functools              import partial
from pprint                 import pprint

from minifold.connector     import Connector
from minifold.filesystem    import check_writable_directory, mtime, mkdir, rm
from minifold.query         import Query, ACTION_READ
from minifold.log           import Log

# TODO:
# For the moment the cache is class-name based. It should rather
# be identify by the connector setup and the underlying connectors
# (if any)

# TODO:
# For the moment, the cache is only used if the exact same Query
# was issued over the past. But we should be able to reuse the cache
# if a less strict query has been issued, and use
# Connector.reshape_entries afterwards.

class CacheConnector(Connector):
    def __init__(self, child):
        self.child = child

    def attributes(self, object :str) -> set:
        return self.child.attributes(object)

    def callback_read(self, query): # raises RuntimeError
        raise RuntimeError("Must be overloaded")

    def callback_write(self, query, data): # raises RuntimeError
        raise RuntimeError("Must be overloaded")

    def clear_query(self, query :Query):
        pass

    def clear_cache(self):
        pass

    def read(self, query :Query):
        (data, success) = (None, False)
        try:
            data = self.callback_read(query)
            success = (data != None)
        except:
            Log.error(
                "CacheConnector.read(%s): Cannot read cache:\n%s" % (
                    query,
                    traceback.format_exc()
                )
            )
        return (data, success)

    def write(self, query :Query, data) -> bool:
        success = True
        try:
            self.callback_write(query, data)
        except:
            Log.error(
                "CacheConnector.write(%s, %s): Cannot write cache:\n%s" % (
                    traceback.format_exc(),
                    query,
                    data
                )
            )
            success = False
        return success

    def is_cached(self, query :Query) -> bool:
        raise RuntimeError("Must be overloaded")

    def is_cachable(self, query :Query, data) -> bool:
        return True

    def query(self, query :Query):
        (data, success) = (None, False)
        if self.is_cached(query):
            (data, success) = self.read(query)
            if not success:
                Log.warning("CacheConnector.query(%s): Unreadable cache" % query)
        if not success:
            data = self.child.query(query)
        if query.action == ACTION_READ and self.is_cachable(query, data):
            self.write(query, data)
        return self.answer(query, data)

# Default parameters, used to initialize StorageCacheConnector class members.
DEFAULT_CACHE_STORAGE_BASE_DIR = os.path.join(os.path.expanduser("~"), ".minifold", "cache")
DEFAULT_CACHE_STORAGE_LIFETIME = datetime.timedelta(days = 3)

def make_cache_dir(base_dir :str, sub_dir :str = ""):
    return os.path.join(base_dir, sub_dir) if sub_dir else base_dir

class StorageCacheConnector(CacheConnector):
    base_dir = DEFAULT_CACHE_STORAGE_BASE_DIR
    lifetime = DEFAULT_CACHE_STORAGE_LIFETIME

    def __init__(
        self,
        child :Connector,
        callback_load = None,
        callback_dump = None,
        lifetime   :datetime.timedelta = None,
        cache_dir  :str = None,
        read_mode  :str = "r",
        write_mode :str = "w",
        extension  :str = ""
    ):
        super().__init__(child)
        self.callback_load = callback_load
        self.callback_dump = callback_dump
        self.lifetime   = lifetime if lifetime is not None else StorageCacheConnector.lifetime
        self.cache_dir  = cache_dir if cache_dir else \
                          make_cache_dir(StorageCacheConnector.base_dir, child.__class__.__name__)
        self.read_mode  = read_mode
        self.write_mode = write_mode
        self.extension  = extension

    def make_cache_filename(self, query :Query) -> str:
        return os.path.join(self.cache_dir, str(query) + self.extension)

    def clear_query(self, query :Query):
        cache_filename = self.make_cache_filename(query)
        if os.path.exists(cache_filename):
            Log.debug("StorageCacheConnector: Removing query [%s]" % cache_filename)
            rm(cache_filename)

    def clear_cache(self):
        if os.path.exists(self.cache_dir) and os.path.isdir(self.cache_dir):
            Log.debug("StorageCacheConnector: Removing cache [%s]" % self.cache_dir)
            rm(self.cache_dir, recursive=True)

    @staticmethod
    def is_fresh_cache(cache_filename :str, lifetime :datetime.timedelta) -> bool:
        is_fresh = True
        if lifetime:
            t_now = datetime.datetime.utcnow()
            t_cache = mtime(cache_filename)
            is_fresh = (t_now - t_cache) < lifetime
            #Log.debug("t_now(%s) - t_cache(%s) = %s ?< lifetime %s" % (
            #    t_now, t_cache, (t_now - t_cache), lifetime
            #))
        return is_fresh

    def is_cached(self, query :Query) -> bool:
        ret = False
        cache_filename = self.make_cache_filename(query)
        if os.path.exists(cache_filename):
            ret = StorageCacheConnector.is_fresh_cache(cache_filename, self.lifetime)
        return ret

    def callback_read(self, query :Query) -> tuple:
        data = None
        cache_filename = self.make_cache_filename(query)
        if self.is_cached(query):
            with open(cache_filename, self.read_mode) as f:
                data = self.callback_load(f)
            Log.debug("Cache hit: [%s]" % cache_filename)
        return data

    def callback_write(self, query :Query, data):
        cache_filename = self.make_cache_filename(query)
        directory = os.path.dirname(cache_filename)
        mkdir(directory)
        check_writable_directory(directory)
        with open(cache_filename, self.write_mode) as f:
            self.callback_dump(data, f)

class PickleCacheConnector(StorageCacheConnector):
    def __init__(
        self,
        child     :Connector,
        lifetime  :datetime.timedelta = StorageCacheConnector.lifetime,
        cache_dir :str                = None
    ):
        super().__init__(
            child,
            pickle.load, pickle.dump,
            lifetime, cache_dir,
            "rb", "wb", ".pkl"
        )

class JsonCacheConnector(StorageCacheConnector):
    def __init__(
        self,
        child     :Connector,
        lifetime  :datetime.timedelta = StorageCacheConnector.lifetime,
        cache_dir :str                = None
    ):
        super().__init__(
            child,
            json.load, partial(json.dump, indent=4),
            lifetime, cache_dir,
            "r", "w", ".json"
        )


