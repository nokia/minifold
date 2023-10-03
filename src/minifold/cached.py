#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import json
import os
import pickle
from functools import partial
from .entries_connector import EntriesConnector
from .filesystem import mkdir
from .log import Log


class CachedEntriesConnector(EntriesConnector):
    """
    :py:class:`CachedEntriesConnector` is a :py:class:`Connector` is an
    abstract class used to fetch data from a cache saved on the local storage.

    See specializations:

    - :py:class:`JsonCachedConnector` (caching using a JSON file)
    - :py:class:`PickleCachedConnector` (caching using pickles)
    """
    def __init__(
        self,
        load_entries: callable,
        cache_filename: str,
        load_cache: callable,
        save_cache: callable,
        read_mode: str,
        write_mode: str,
        with_cache: bool = True
    ):
        """
        Constructor.

        Args:
            load_entries (callable): A function called to populate this
                :py:class:`CachedEntriesConnector`.
            cache_filename (str): The path to the file used to save the
                cache on the local storage.
            load_cache (callable): A function `entries = load_cache(f)` where:
                `entries` is a list of dictionnaries;
                `f` is the (read) file descriptor of the cache.
            save_cache (callable): A function `save_cache(cache_filename, f)` where:
                `entries` is a list of dictionnaries;
                `f` is the (write) file descriptor of the cache.
            read_mode (str): A string specifying how the read file decriptor of the
                cache must be created. Possible values are ``"r"`` (text-based cache)
                and ``"rb"`` (binary cache).
            write_mode (str): A string specifying how the write file decriptor of the
                cache must be created. Possible values are ``"w"`` (text-based cache)
                and ``"wb"`` (binary cache).
        """
        loaded_from_cache = False
        if with_cache:
            try:
                with open(cache_filename, read_mode) as f:
                    Log.info("%s: Loading cache from [%s]" % (type(self), cache_filename))
                    entries = load_cache(f)
                    Log.info("Loaded %d entries" % len(entries))
                    loaded_from_cache = True
            except FileNotFoundError:
                Log.debug("%s: Cache [%s] not found" % (type(self), cache_filename))
                pass
            except Exception as e:
                Log.debug("%s: Cache [%s] corrupted" % (type(self), cache_filename))
                Log.error(e)
                pass

        # Parse the input data (if needed)
        if not loaded_from_cache:
            entries = load_entries()
            Log.info("Loaded %d entries" % len(entries))

        # Save into cache (if needed)
        if with_cache and not loaded_from_cache:
            Log.info("%s: Saving data into cache [%s]" % (type(self), cache_filename))
            mkdir(os.path.dirname(cache_filename))
            with open(cache_filename, write_mode) as f:
                save_cache(entries, f)

        super().__init__(entries)


class JsonCachedConnector(CachedEntriesConnector):
    """
    The :py:class:`JsonCachedConnector` class implements the
    :py:class:`CachedEntriesConnector` using a tierce JSON file.
    """
    def __init__(self, load_entries: callable, cache_filename: str, **kwargs):
        """
        Constructor.
        See also :py:class:`CachedEntriesConnector.__init__`

        Args:
            load_entries (callable): A function called to populate this
                :py:class:`CachedEntriesConnector`.
            cache_filename (str): The path to the file used to save the
                cache on the local storage.
        """
        super().__init__(
            load_entries,
            cache_filename,
            load_cache=json.load,
            save_cache=partial(json.dump, indent=4),
            read_mode="r",
            write_mode="w",
            **kwargs
        )


class PickleCachedConnector(CachedEntriesConnector):
    """
    The :py:class:`PickleCachedConnector` class implements the
    :py:class:`CachedEntriesConnector` using a tierce pickle file.
    """
    def __init__(self, load_entries: callable, cache_filename: str, **kwargs):
        """
        Constructor.
        See also :py:class:`CachedEntriesConnector.__init__`

        Args:
            load_entries (callable): A function called to populate this
                :py:class:`CachedEntriesConnector`.
            cache_filename (str): The path to the file used to save the
                cache on the local storage.
        """
        super().__init__(
            load_entries,
            cache_filename,
            load_cache=pickle.load,
            save_cache=pickle.dump,
            read_mode="rb",
            write_mode="wb",
            **kwargs
        )
