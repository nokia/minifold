#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from pprint import pformat
from minifold.binary_predicate import BinaryPredicate
from minifold.entries_connector import EntriesConnector
from minifold.log import Log
from minifold.query import Query

Log.enable_print = True

ENTRIES = [
    {'a' : 1,   'b' : 2,   'c' : 3},
    {'a' : 10,  'b' : 20,  'c' : 30},
    {'a' : 100, 'b' : 200, 'c' : 300},
    {'a' : 100, 'b' : 200, 'd' : 400},
]

def test_query_select_where():
    entries_connector = EntriesConnector(ENTRIES)
    q = Query(
        attributes = ["a", "c", "d"],
        filters = BinaryPredicate(
            BinaryPredicate("a", "<=", 100),
            "&&",
            BinaryPredicate("b", ">", 20)
        )
    )
    result = entries_connector.query(q)

    assert result == [
        {'a': 100, 'c': 300, 'd': None},
        {'a': 100, 'c': None, 'd': 400}
    ]

def test_offset_limit():
    entries_connector = EntriesConnector(ENTRIES)
    attributes = ["a", "b", "c"]
    for offset in range(len(ENTRIES)):
        for limit in range(len(ENTRIES)):
            q = Query(
                attributes = attributes,
                offset = offset,
                limit = limit
            )
            Log.debug(q)
            result = entries_connector.query(q)
            Log.debug(pformat(result))

            assert len(result) == min(limit, len(ENTRIES) - offset),\
                "Invalid #entries for %s:\n%s" % (str(q), pformat(result))
            expected = [
                {k : entry.get(k) for k in attributes}
                for entry in ENTRIES[offset : offset + limit]
            ]
            assert result == expected, """
                Got      : %s\n
                Expected : %s\n
            """ % (result, expected)
