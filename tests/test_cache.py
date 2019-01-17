#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import datetime
from pprint                         import pformat
from time                           import sleep

from minifold.binary_predicate      import BinaryPredicate
from minifold.cache                 import JsonCacheConnector, PickleCacheConnector
from minifold.entries_connector     import EntriesConnector
from minifold.log                   import Log
from minifold.query                 import Query

Log.enable_print = True

ENTRIES = [
    {"a" : 1,   "b" : 2,   "c" : 3},
    {"a" : 10,  "b" : 20,  "c" : 30},
    {"a" : 100, "b" : 200, "c" : 300},
    {"a" : 100, "b" : 200, "d" : 400},
]

CACHE_CONNECTORS = [
    PickleCacheConnector(EntriesConnector(ENTRIES)),
    JsonCacheConnector  (EntriesConnector(ENTRIES))
]

SHORT_LIFETIME = datetime.timedelta(milliseconds = 50)

CACHE_CONNECTORS_SHORT_LIFETIME = [
    PickleCacheConnector(EntriesConnector(ENTRIES), lifetime=SHORT_LIFETIME),
    JsonCacheConnector  (EntriesConnector(ENTRIES), lifetime=SHORT_LIFETIME)
]


def test_clear_query():
    for cache_connector in CACHE_CONNECTORS:
        query = Query()
        cache_connector.clear_query(query)
        assert cache_connector.is_cached(query) == False

def test_clear_cache():
    queries = [Query(), Query(attributes = ("a",))]
    for cache_connector in CACHE_CONNECTORS:
        for query in queries:
            cache_connector.query(query)
        for query in queries:
            assert cache_connector.is_cached(query) == True
        cache_connector.clear_cache()
        for query in queries:
            assert cache_connector.is_cached(query) == False

def test_simple_query():
    query = Query()
    for cache_connector in CACHE_CONNECTORS:
        cache_connector.clear_query(query)
        assert cache_connector.is_cached(query) == False
        obtained = cache_connector.query(query)
        assert cache_connector.is_cached(query) == True
        assert len(obtained) == len(ENTRIES)

        # Note: obtained and ENTRIES may slightly differ (missing attributes set to None)
        for i in range(len(obtained)):
            for k in ["a", "b", "c", "d"]:
                assert obtained[i].get(k) == ENTRIES[i].get(k)

def test_query_select_where():
    query = Query(
        attributes = ["a", "c", "d"],
        filters    = BinaryPredicate(
            BinaryPredicate("a", "<=", 100),
            "&&",
            BinaryPredicate("b", ">", 20)
        )
    )

    expected = [
        {"a": 100, "c": 300,  "d": None},
        {"a": 100, "c": None, "d": 400}
    ]

    for cache_connector in CACHE_CONNECTORS:
        Log.info("Clearing cache" + ("-" * 80))
        cache_connector.clear_query(query)

        Log.info("Non-cached query" + ("-" * 80))
        Log.info("Check if not cached")
        assert cache_connector.is_cached(query) == False

        Log.info("Query")
        result = cache_connector.query(query)
        assert result == expected

        Log.info("Cached query" + ("-" * 80))
        Log.info("Check if cached")
        assert cache_connector.is_cached(query) == True

        Log.info("Query")
        result = cache_connector.query(query)
        assert result == expected

def test_cache_lifetime():
    query = Query()
    for cache_connector in CACHE_CONNECTORS_SHORT_LIFETIME:
        query = Query()
        cache_connector.clear_query(query)
        assert cache_connector.is_cached(query) == False
        cache_connector.query(query)
        assert cache_connector.is_cached(query) == True
        sleep(SHORT_LIFETIME.total_seconds())
        assert cache_connector.is_cached(query) == False

def test_offset_limit():
    for cache_connector in CACHE_CONNECTORS:
        attributes = ("a", "b", "c")
        for offset in range(len(ENTRIES)):
            for limit in range(len(ENTRIES)):
                query = Query(
                    attributes = attributes,
                    offset     = offset,
                    limit      = limit
                )
                Log.info(query)
                result = cache_connector.query(query)
                Log.info(pformat(result))

                assert len(result) == min(limit, len(ENTRIES) - offset),\
                    "Invalid #entries for %s:\n%s" % (str(query), pformat(result))
                expected = [
                    {k : entry.get(k) for k in attributes} \
                    for entry in ENTRIES[offset : offset + limit]
                ]
                assert result == expected, """
                    Got      : %s\n
                    Expected : %s\n
                """ % (result, expected)
