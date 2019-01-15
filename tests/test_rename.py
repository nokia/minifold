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

from minifold.binary_predicate      import BinaryPredicate
from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query
from minifold.rename                import RenameConnector

ENTRIES = [
    {"a" : 1,   "b" : 2,   "c" : 3},
    {"a" : 10,  "b" : 20,  "c" : 30},
    {"a" : 100, "b" : 200, "c" : 300},
    {"a" : 100, "b" : 200, "d" : 400},
]

MAP_RENAME = {
    "a" : "A",
    "b" : "B",
    "c" : "C",
    "d" : "D",
}

def test_rename_select_where():
    rename_connector = RenameConnector(
        MAP_RENAME,
        EntriesConnector(ENTRIES)
    )
    query = Query(
        attributes = ["A", "C", "D"],
        filters    = BinaryPredicate(BinaryPredicate("A", "<=", 100), "&&", BinaryPredicate("B", ">", 20))
    )
    result = rename_connector.query(query)

    assert result == [
        {"A": 100, "C": 300,  "D": None},
        {"A": 100, "C": None, "D": 400}
    ]


