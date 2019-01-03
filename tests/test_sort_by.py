#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query
from minifold.sort_by               import sort_by, SortByConnector

ENTRIES = [
    {"a" : 1,    "b" : 200, "c" : 31},
    {"a" : 1,    "b" : 250, "c" : 3},
    {"a" : 10,   "b" : 200, "c" : 300},
    {"a" : 100,  "b" : 2,   "c" : 30},
]

EXPECTED_ASC = {
    "a" : [
        {"a": 1,   "b": 200, "c": 31},
        {"a": 1,   "b": 250, "c": 3},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 100, "b": 2,   "c": 30}
    ],
    "b" : [
        {"a": 100, "b": 2,   "c": 30},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 1,   "b": 250, "c": 3}
    ],
    "c" : [
        {"a": 1,   "b": 250, "c": 3},
        {"a": 100, "b": 2,   "c": 30},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 10,  "b": 200, "c": 300}
    ],
    ("a", "b") : [
        {"a": 1,   "b": 200, "c": 31},
        {"a": 1,   "b": 250, "c": 3},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 100, "b": 2,   "c": 30}
    ],
    ("b", "a") : [
        {"a": 100, "b": 2,   "c": 30},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 1,   "b": 250, "c": 3}
    ],
}

EXPECTED_DESC = {
    "a" : [
        {"a": 100, "b": 2,   "c": 30},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 1,   "b": 250, "c": 3}
    ],
    "b" : [
        {"a": 1,   "b": 250, "c": 3},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 100, "b": 2,   "c": 30}
    ],
    "c" : [
        {"a": 10,  "b": 200, "c": 300},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 100, "b": 2,   "c": 30},
        {"a": 1,   "b": 250, "c": 3}
    ],
    ("a", "b") : [
        {"a": 100, "b": 2,   "c": 30},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 1,   "b": 250, "c": 3},
        {"a": 1,   "b": 200, "c": 31}
    ],
    ("b", "a") : [
        {"a": 1,   "b": 250, "c": 3},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 100, "b": 2,   "c": 30}
    ],
}

def test_sort_by_asc():
    for k in ["a", "b", "c", ("a", "b"), ("b", "a")]:
        obtained = sort_by(k if isinstance(k, tuple) else [k], ENTRIES)
        assert obtained == EXPECTED_ASC[k]

def test_sort_by_desc():
    for k in ["a", "b", "c", ("a", "b"), ("b", "a")]:
        obtained = sort_by(k if isinstance(k, tuple) else [k], ENTRIES, True)
        assert obtained == EXPECTED_DESC[k]

def test_sort_by_connector():
    sort_by_connector = SortByConnector(
        ("b", "a"),
        EntriesConnector(ENTRIES)
    )
    obtained = sort_by_connector.query(Query())
    assert obtained == [
        {"a": 100, "b": 2, "c": 30},
        {"a": 1,   "b": 200, "c": 31},
        {"a": 10,  "b": 200, "c": 300},
        {"a": 1,   "b": 250, "c": 3}
    ]
