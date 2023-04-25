#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.count import CountConnector, count
from minifold.entries_connector import EntriesConnector
from minifold.query import Query
from minifold.union import UnionConnector, union

ENTRIES = [
    {"a": 1, "b": 2, "c": 3},
    {"a": 10, "b": 20, "c": 30},
    {"a": 100, "b": 200, "c": 300},
    {"a": 100, "b": 200, "d": 400},
]

ENTRIES_CONNECTOR = EntriesConnector(ENTRIES)
EMPTY_CONNECTOR = EntriesConnector([])

def test_union():
    assert union([ENTRIES, []]) == ENTRIES
    assert union([[], ENTRIES]) == ENTRIES
    assert union([ENTRIES, ENTRIES]) == ENTRIES + ENTRIES

def test_union_connector_empty():
    union_connector = UnionConnector([
        ENTRIES_CONNECTOR,
        EMPTY_CONNECTOR
    ])
    union_connector.query(Query()) == ENTRIES

def test_union_connector_duplicates():
    union_connector = UnionConnector([
        ENTRIES_CONNECTOR,
        ENTRIES_CONNECTOR
    ])
    union_connector.query(Query()) == ENTRIES + ENTRIES
