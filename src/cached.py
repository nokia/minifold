#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#This file is part of newdle
#Copyright © 2018 Nokia Corporation and/or its subsidiary(-ies). All rights reserved. *
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import json, os, partial, pickle
from minifold.cache             import DEFAULT_CACHE_STORAGE_BASE_DIR
from minifold.entries_connector import EntriesConnector
from minifold.filesystem        import mkdir
from minifold.cache             import JsonCacheConnector
from minifold.log               import Log

class CachedEntriesConnector(EntriesConnector):
    def __init__(
        self,
        load_entries,
        cache_filename :str,
        load_cache,
        save_cache,
        read_mode,
        write_mode,
        with_cache :bool = True
    ):
        loaded_from_cache = False
        if with_cache:
            try:
                with open(cache_filename, read_mode) as f:
                    Log.info("%s: Loading cache from [%s]" % (type, cache_filename))
                    entries = load_cache(f)
                    Log.info("Loaded %d entries" % len(entries))
                    loaded_from_cache = True
            except FileNotFoundError:
                Log.debug("%s: Cache [%s] not found" % (type, cache_filename))
                pass
            except Exception as e:
                Log.debug("%s: Cache [%s] corrupted" % (type, cache_filename))
                Log.error(e)
                pass

        # Parse the input data (if needed)
        if not loaded_from_cache:
            entries = load_entries()
            Log.info("Loaded %d entries" % len(entries))

        # Save into cache (if needed)
        if with_cache and not loaded_from_cache:
            Log.info("%s: Saving data into cache [%s]" % (type, cache_filename))
            mkdir(os.path.dirname(cache_filename))
            with open(cache_filename, write_mode) as f:
                save_cache(entries, f)

        super().__init__(entries)

class JsonCachedConnector(CachedEntriesConnector):
    def __init__(self, load_entries, cache_filename :str, **kwargs):
        super().__init__(
            load_entries,
            cache_filename,
            load_cache = json.load,
            save_cache = partial(json.dump, indent=4),
            read_mode  = "r",
            write_mode = "w",
            **kwargs
        )

class PickleCachedEntriesConnector(CachedEntriesConnector):
    def __init__(self, load_entries, cache_filename :str, **kwargs):
        super().__init__(
            load_entries,
            cache_filename,
            load_cache = pickle.load,
            save_cache = pickle.dump,
            read_mode  = "rb",
            write_mode = "wb",
            **kwargs
        )
