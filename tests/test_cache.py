#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import datetime
from pprint import pformat
from time import sleep

from minifold.binary_predicate import BinaryPredicate
from minifold.cache import (
    DEFAULT_CACHE_STORAGE_BASE_DIR, StorageCacheConnector,
    JsonCacheConnector, PickleCacheConnector
)
from minifold.entries_connector import EntriesConnector
from minifold.log import Log
from minifold.query import Query

Log.enable_print = True

ENTRIES = [
    {"a": 1, "b": 2, "c": 3},
    {"a": 10, "b": 20, "c": 30},
    {"a": 100, "b": 200, "c": 300},
    {"a": 100, "b": 200, "d": 400},
]

STORAGE_CONNECTOR_CLASSES = [PickleCacheConnector, JsonCacheConnector]
CACHE_CONNECTORS = [
    cls(EntriesConnector(ENTRIES))
    for cls in STORAGE_CONNECTOR_CLASSES
]


def test_clear_query():
    for cache_connector in CACHE_CONNECTORS:
        query = Query()
        cache_connector.clear_query(query)
        assert cache_connector.is_cached(query) is False


def test_clear_cache():
    queries = [Query(), Query(attributes=("a", ))]
    for cache_connector in CACHE_CONNECTORS:
        for query in queries:
            cache_connector.query(query)
        for query in queries:
            assert cache_connector.is_cached(query) is True
        cache_connector.clear_cache()
        for query in queries:
            assert cache_connector.is_cached(query) is False


def test_simple_query():
    query = Query()
    for cache_connector in CACHE_CONNECTORS:
        cache_connector.clear_query(query)
        assert cache_connector.is_cached(query) is False
        obtained = cache_connector.query(query)
        assert cache_connector.is_cached(query) is True
        assert len(obtained) == len(ENTRIES)

        # Note: obtained and ENTRIES may slightly differ (missing attributes set to None)
        for i in range(len(obtained)):
            for k in ["a", "b", "c", "d"]:
                assert obtained[i].get(k) == ENTRIES[i].get(k)


def test_query_select_where():
    query = Query(
        attributes=["a", "c", "d"],
        filters=BinaryPredicate(
            BinaryPredicate("a", "<=", 100),
            "&&",
            BinaryPredicate("b", ">", 20)
        )
    )

    expected = [
        {"a": 100, "c": 300, "d": None},
        {"a": 100, "c": None, "d": 400}
    ]

    for cache_connector in CACHE_CONNECTORS:
        Log.info("Clearing cache" + ("-" * 80))
        cache_connector.clear_query(query)

        Log.info("Non-cached query" + ("-" * 80))
        Log.info("Check if not cached")
        assert cache_connector.is_cached(query) is False

        Log.info("Query")
        result = cache_connector.query(query)
        assert result == expected

        Log.info("Cached query" + ("-" * 80))
        Log.info("Check if cached")
        assert cache_connector.is_cached(query) is True

        Log.info("Query")
        result = cache_connector.query(query)
        assert result == expected


def test_cache_lifetime():
    short_lifetime = datetime.timedelta(milliseconds=50)
    cache_connectors_short_lifetime = [
        cls(EntriesConnector(ENTRIES), lifetime=short_lifetime)
        for cls in STORAGE_CONNECTOR_CLASSES
    ]

    query = Query()
    for cache_connector in cache_connectors_short_lifetime:
        query = Query()
        cache_connector.clear_query(query)
        assert cache_connector.is_cached(query) is False
        cache_connector.query(query)
        assert cache_connector.is_cached(query) is True
        sleep(short_lifetime.total_seconds())
        assert cache_connector.is_cached(query) is False


def test_offset_limit():
    for cache_connector in CACHE_CONNECTORS:
        attributes = ("a", "b", "c")
        for offset in range(len(ENTRIES)):
            for limit in range(len(ENTRIES)):
                query = Query(
                    attributes=attributes,
                    offset=offset,
                    limit=limit
                )
                Log.info(query)
                result = cache_connector.query(query)
                Log.info(pformat(result))

                assert len(result) == min(limit, len(ENTRIES) - offset),\
                    "Invalid #entries for %s:\n%s" % (str(query), pformat(result))
                expected = [
                    {k: entry.get(k) for k in attributes}
                    for entry in ENTRIES[offset: offset + limit]
                ]
                assert result == expected, """
                    Got      : %s\n
                    Expected : %s\n
                """ % (result, expected)


def test_cache_rebase():
    DUMMY_BASE_DIR = "/tmp/.minifold"

    def check_base_dir(cache_connectors: list, dummy_cache_connectors: list = list()):
        query = Query()
        for cache_connector in cache_connectors:
            cache_filename = cache_connector.make_cache_filename(query)
            Log.debug(cache_filename)
            assert cache_filename.startswith(DEFAULT_CACHE_STORAGE_BASE_DIR)
        for dummy_cache_connector in dummy_cache_connectors:
            cache_filename = dummy_cache_connector.make_cache_filename(query)
            Log.debug(cache_filename)
            assert cache_filename.startswith(DUMMY_BASE_DIR)

    # CACHE_CONNECTORS should be stored in DEFAULT_CACHE_STORAGE_BASE_DIR.
    check_base_dir(CACHE_CONNECTORS, [])

    # We now rebase the default cache directory to DUMMY_BASE_DIR.
    # Caches newly created should be stored in DUMMY_BASE_DIR but the caches
    # previously created should remain in their place.
    Log.info("Setting StorageCacheConnector.base_dir to [%s]" % DUMMY_BASE_DIR)
    StorageCacheConnector.base_dir = DUMMY_BASE_DIR
    dummy_cache_connectors = [
        cls(EntriesConnector(ENTRIES))
        for cls in STORAGE_CONNECTOR_CLASSES
    ]

    check_base_dir(CACHE_CONNECTORS, dummy_cache_connectors)

    # We now rebase the default cache directory the standard cache directory.
    # Caches newly created should be stored in DEFAULT_CACHE_STORAGE_BASE_DIR but the caches
    # previously created should remain in their place.
    Log.info("Setting StorageCacheConnector.base_dir to [%s]" % DEFAULT_CACHE_STORAGE_BASE_DIR)
    StorageCacheConnector.base_dir = DEFAULT_CACHE_STORAGE_BASE_DIR

    check_base_dir(CACHE_CONNECTORS, dummy_cache_connectors)
