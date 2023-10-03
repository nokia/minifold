#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.binary_predicate import BinaryPredicate
from minifold.entries_connector import EntriesConnector
from minifold.query import Query
from minifold.where import where, WhereConnector


ENTRIES = [
    {"a": 1, "b": 2, "c": 3},
    {"a": 10, "b": 20, "c": 30},
    {"a": 100, "b": 200, "c": 300}
]


def KEEP_IF(entry: dict) -> bool:
    return entry["a"] <= 10 and entry["c"] > 0


EXPECTED = [
    {"a": 1, "b": 2, "c": 3},
    {"a": 10, "b": 20, "c": 30}
]


def test_where():
    obtained = where(ENTRIES, KEEP_IF)
    assert obtained == EXPECTED


def test_where_on_entries_connector():
    entries_connector = EntriesConnector(ENTRIES)
    obtained = entries_connector.query(
        Query(
            filters=BinaryPredicate(
                BinaryPredicate("a", "<=", 10),
                "&&",
                BinaryPredicate("c", ">", 0)
            )
        )
    )
    assert obtained == EXPECTED


def test_where_connector():
    entries_connector = EntriesConnector(ENTRIES)
    where_connector = WhereConnector(entries_connector, KEEP_IF)
    obtained = where_connector.query(Query())
    assert obtained == EXPECTED
