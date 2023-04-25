#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.binary_predicate import BinaryPredicate
from minifold.entries_connector import EntriesConnector
from minifold.query import Query
from minifold.rename import RenameConnector

ENTRIES = [
    {"a": 1,   "b": 2,   "c": 3},
    {"a": 10,  "b": 20,  "c": 30},
    {"a": 100, "b": 200, "c": 300},
    {"a": 100, "b": 200, "d": 400},
]

MAP_RENAME = {
    "a": "A",
    "c": "C",
    "d": "D",
}

RENAME_CONNECTOR = RenameConnector(
    MAP_RENAME,
    EntriesConnector(ENTRIES)
)

def test_rename_select_where():
    query = Query(
        attributes = ["A", "C", "D"],
        filters = BinaryPredicate(
            BinaryPredicate("A", "<=", 100),
            "&&",
            BinaryPredicate("b", ">", 20)
        )
    )
    obtained = RENAME_CONNECTOR.query(query)

    assert obtained == [
        {"A": 100, "C": 300, "D": None},
        {"A": 100, "C": None, "D": 400}
    ]

def test_rename_attributes():
    obtained = RENAME_CONNECTOR.attributes(None)
    assert obtained == {"A", "b", "C", "D"}
