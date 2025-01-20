#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import datetime
import json
import os
import pickle
import traceback

from functools import partial

from .connector import Connector
from .filesystem import check_writable_directory, mtime, mkdir, rm
from .query import Query, ACTION_READ
from .log import Log


class CacheConnector(Connector):
    """
    :py:class:`CacheConnector` is a :py:class:`Connector` is an
    abstract class used to cache results in the middle of a
    minifold query plan.
    If a query reaches this :py:class:`CacheEntriesConnector` and is
    in cache, it is not forwarded to the underlying connector, hence
    accelerating the query plan execution.

    See specializations:

    - :py:class:`StorageCacheConnector` (caching using a local file)
    - :py:class:`JsonCacheConnector` (caching using a local JSON file)
    - :py:class:`PickleCacheConnector` (caching using a local pickle file)

    Possible improvements:

    - For the moment the cache is class-name based. It should rather
      be identify by the connector setup and the underlying connectors
      (if any)
    - For the moment, the cache is only used if the exact same Query
      was issued over the past. But we should be able to reuse the cache
      if a less strict query has been issued, and use
      Connector.reshape_entries afterwards.
    """
    def __init__(self, child):
        """
        Constructor.
        """
        self.child = child

    def attributes(self, object: str) -> set:
        """
        Retrieves the keys supported by this
        :py:class:`CacheEntriesConnector` instance.

        Returns:
            The key of the underlying entries.
        """
        return self.child.attributes(object)

    def callback_read(self, query: Query) -> object:
        """
        Callback triggered when data must be fetched in this
        :py:class:`CacheEntriesConnector`.

        Args:
            query (Query): The handled :py:class:`Query` instance.

        Raise:
            RuntimeError: if not overloaded.

        Returns:
            The fetched data.
        """
        raise RuntimeError("Must be overloaded")

    def callback_write(self, query: Query, data: object):
        """
        Callback triggered when data must be saved in this
        :py:class:`CacheEntriesConnector` instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.
            data (object): The data to be saved.

        Raise:
            RuntimeError: if not overloaded.
        """
        raise RuntimeError("Must be overloaded")

    def clear_query(self, query: Query):
        """
        Removes a :py:class:`Query` result from this
        :py:class:`CacheEntriesConnector` instance.
        This method should be overloaded.

        Args:
            query (Query): The handled :py:class:`Query` instance.
        """
        pass

    def clear_cache(self):
        """
        Clears this :py:class:`CacheEntriesConnector` instance entirely.
        This method should be overloaded.
        """
        pass

    def read(self, query: Query) -> object:
        """
        Fetches from this :py:class:`CacheEntriesConnector` instance the corresponding data.

        Returns:
            The corresponding cached object.
        """
        (data, success) = (None, False)
        try:
            data = self.callback_read(query)
            success = (data is not None)
        except Exception:
            Log.error(
                "CacheConnector.read(%s): Cannot read cache:\n%s" % (
                    query,
                    traceback.format_exc()
                )
            )
        return (data, success)

    def write(self, query: Query, data: object) -> bool:
        """
        Writes data to this :py:class:`CacheEntriesConnector` instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.
            data (object): The data fetched by this :py:class:`Query` that must be
                saved to this :py:class:`CacheEntriesConnector` instance.

        Returns:
            The corresponding cached object.
        """
        success = True
        try:
            self.callback_write(query, data)
        except Exception:
            Log.error(
                "CacheConnector.write(%s, %s): Cannot write cache:\n%s" % (
                    traceback.format_exc(),
                    query,
                    data
                )
            )
            success = False
        return success

    def is_cached(self, query: Query) -> bool:
        """
        Checks whether a :py:class:`Query` instance is already cached in this
        :py:class:`CacheEntriesConnector` instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.

        Returns:
            ``True`` if ``query`` is cached in this
            :py:class:`CacheEntriesConnector` instance,
            ``False`` otherwise.
        """
        raise RuntimeError("Must be overloaded")

    def is_cachable(self, query: Query, data: object) -> bool:
        """
        Checks whether a data may be saved in this
        :py:class:`CacheEntriesConnector` instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.
            data (object): The data fetched by this :py:class:`Query` that
                must be saved to this :py:class:`CacheEntriesConnector`
                instance.

        Returns:
            ``True`` if ``query`` may be cached in this
            :py:class:`CacheEntriesConnector` instance,
            ``False`` otherwise.
        """
        return True

    def query(self, query: Query) -> list:
        """
        Handles an incoming :py:class:`Query` instance.

        The :py:class:`CacheEntriesConnector` checks whether it is already
        cached. If ``query`` is cached in this
        :py:class:`CacheEntriesConnector`, it is not forwarded to
        :py:attr:`self.child` and the results are directly from the cache.
        Otherwise, it is forwarded to :py:attr:`self.child`.

        Args:
            query (Query): The handled :py:class:`Query` instance.

        Returns:
            The corresponding entries.
        """
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
DEFAULT_CACHE_STORAGE_BASE_DIR = os.path.join(
    os.path.expanduser("~"),
    ".minifold",
    "cache"
)
DEFAULT_CACHE_STORAGE_LIFETIME = datetime.timedelta(days=3)


def make_cache_dir(base_dir: str, sub_dir: str = ""):
    """
    Crafts the path to a minifold cache file.

    Args:
        base_dir (str): The directory storing the minifold caches.
            See also :py:data:`DEFAULT_CACHE_STORAGE_BASE_DIR`.
        sub_dir (str): The directory storing the minifold caches.
            This is often the name assigned to a connector pulling
            remote data.
    """
    return os.path.join(base_dir, sub_dir) if sub_dir else base_dir


class StorageCacheConnector(CacheConnector):
    """
    :py:class:`StorageCacheConnector` is an abstract class
    that specializes of :py:class:`CacheConnector` to manage
    file on the local storage.

    See specializations:

    - :py:class:`JsonCacheConnector` (caching using a local JSON file)
    - :py:class:`PickleCacheConnector` (caching using a local pickle file)
    """
    base_dir = DEFAULT_CACHE_STORAGE_BASE_DIR  # Path to the minifold cache directory
    lifetime = DEFAULT_CACHE_STORAGE_LIFETIME  # Lifetime of the cached objects

    def __init__(
            self,
            child: Connector,
            callback_load: callable = None,
            callback_dump: callable = None,
            lifetime: datetime.timedelta = None,
            cache_dir: str = None,
            read_mode: str = "r",
            write_mode: str = "w",
            extension: str = ""
    ):
        """
        Constructor.

        Args:
            child (Connector): The child :py:class:`Connector` instance.
            callback_load (callable): A function ``callback_load(f)`` where
                ``f`` is the read file descriptor of the cache and which returns
                the cached object.
            callback_dump (callable): A function ``callback_load(data, f)`` where
                ``f`` is the read file descriptor of the cache
                and ``data`` is the object to be cached.
            lifetime (datetime.timedelta): The lifetime of the cached objects.
                Pass ``None`` to use the default lifetime.
            cache_dir (str): The path to the cache directory.
                Pass ``None`` to use the default minifold cache directory.
            read_mode (str): The string specifying how to open the file descriptor
                to read the cache. Possible values are ``"r"`` (text cache)
                and ``"rb"`` (binary cache).
            read_mode (str): The string specifying how to open the file descriptor
                to read the cache. Possible values are ``"r"`` (text cache)
                and ``"rb"`` (binary cache).
            extension (str): The extension of the cache filename.
        """
        super().__init__(child)
        self.callback_load = callback_load
        self.callback_dump = callback_dump
        self.lifetime = (
                lifetime if lifetime is not None
                else StorageCacheConnector.lifetime
        )
        self.cache_dir = (
            cache_dir if cache_dir
            else make_cache_dir(
                StorageCacheConnector.base_dir,
                child.__class__.__name__
            )
        )
        self.read_mode = read_mode
        self.write_mode = write_mode
        self.extension = extension

    def make_cache_filename(self, query: Query) -> str:
        """
        Crafts the filename of the cache to store a given :py:class:`Query`
        instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.

        Returns:
            The corresponding filename.
        """
        return os.path.join(self.cache_dir, str(query) + self.extension)

    def clear_query(self, query: Query):
        """
        Removes a :py:class:`Query` result from this
        :py:class:`StorageCacheConnector` instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.
        """
        cache_filename = self.make_cache_filename(query)
        if os.path.exists(cache_filename):
            Log.debug("StorageCacheConnector: Removing query [%s]" % cache_filename)
            rm(cache_filename)

    def clear_cache(self):
        """
        Clears this :py:class:`CacheEntriesConnector` instance entirely.
        """
        if os.path.exists(self.cache_dir) and os.path.isdir(self.cache_dir):
            Log.debug("StorageCacheConnector: Removing cache [%s]" % self.cache_dir)
            rm(self.cache_dir, recursive=True)

    @staticmethod
    def is_fresh_cache(cache_filename: str, lifetime: datetime.timedelta) -> bool:
        """
        Checks whether a minifold cache file is fresh enough to be relevant.

        To do so, :py:class:`StorageCacheConnector.is_fresh_cache` fetches the
        date of the cache file from the filesystem and matches it against
        ``lifetime``.

        Args:
            cache_filename (str): The path to the cache.
            lifetime (datetime.timedelta): The lifetime of the cache.

        Returns:
            ``True`` if and only if the cache is fresh enough,
            ``False`` otherwise.
        """
        is_fresh = True
        if lifetime:
            t_now = datetime.datetime.now(datetime.UTC)
            t_cache = mtime(cache_filename)
            is_fresh = (t_now - t_cache) < lifetime
            # Log.debug("t_now(%s) - t_cache(%s) = %s ?< lifetime %s" % (
            #    t_now, t_cache, (t_now - t_cache), lifetime
            # ))
        return is_fresh

    def is_cached(self, query: Query) -> bool:
        """
        Checks whether a :py:class:`Query` instance is already cached in this
        :py:class:`StorageCacheConnector` instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.

        Returns:
            ``True`` if ``query`` is cached in this
            :py:class:`StorageCacheConnector` instance,
            ``False`` otherwise.
        """
        ret = False
        cache_filename = self.make_cache_filename(query)
        if os.path.exists(cache_filename):
            ret = StorageCacheConnector.is_fresh_cache(cache_filename, self.lifetime)
        return ret

    def callback_read(self, query: Query) -> object:
        """
        Callback triggered when data must be fetched in this
        :py:class:`StorageCacheConnector`.

        Args:
            query (Query): The handled :py:class:`Query` instance.

        Returns:
            The fetched data.
        """
        data = None
        cache_filename = self.make_cache_filename(query)
        if self.is_cached(query):
            with open(cache_filename, self.read_mode) as f:
                data = self.callback_load(f)
            Log.debug("Cache hit: [%s]" % cache_filename)
        return data

    def callback_write(self, query: Query, data: object):
        """
        Callback triggered when data must be saved in this
        :py:class:`StorageCacheConnector` instance.

        Args:
            query (Query): The handled :py:class:`Query` instance.
            data (object): The data to be saved.
        """
        cache_filename = self.make_cache_filename(query)
        directory = os.path.dirname(cache_filename)
        mkdir(directory)
        check_writable_directory(directory)
        with open(cache_filename, self.write_mode) as f:
            self.callback_dump(data, f)


class PickleCacheConnector(StorageCacheConnector):
    """
    :py:class:`PickleCacheConnector` overloads :py:class:`StorageCacheConnector`
    to cache result in pickle files.
    """
    def __init__(
            self,
            child: Connector,
            lifetime: datetime.timedelta = StorageCacheConnector.lifetime,
            cache_dir: str = None
    ):
        """
        Constructor.

        Args:
            child (Connector): The child :py:class:`Connector` instance.
            lifetime (datetime.timedelta): The lifetime of the cached objects.
                Pass ``None`` to use the default lifetime.
            cache_dir (str): The path to the cache directory.
                Pass ``None`` to use the default minifold cache directory.
        """
        super().__init__(
            child,
            pickle.load, pickle.dump,
            lifetime, cache_dir,
            "rb", "wb", ".pkl"
        )


class JsonCacheConnector(StorageCacheConnector):
    """
    :py:class:`JsonCacheConnector` overloads :py:class:`StorageCacheConnector`
    to cache result in JSON files.
    """
    def __init__(
            self,
            child: Connector,
            lifetime: datetime.timedelta = StorageCacheConnector.lifetime,
            cache_dir: str = None
    ):
        """
        Constructor.

        Args:
            child (Connector): The child :py:class:`Connector` instance.
            lifetime (datetime.timedelta): The lifetime of the cached objects.
                Pass ``None`` to use the default lifetime.
            cache_dir (str): The path to the cache directory.
                Pass ``None`` to use the default minifold cache directory.
        """
        super().__init__(
            child,
            json.load, partial(json.dump, indent=4),
            lifetime, cache_dir,
            "r", "w", ".json"
        )
