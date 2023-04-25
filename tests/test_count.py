#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.count import CountConnector, count
from minifold.entries_connector import EntriesConnector
from minifold.binary_predicate  import BinaryPredicate
from minifold.query import Query

ENTRIES = [
    {'a' : 1,   'b' : 2,   'c' : 3},
    {'a' : 10,  'b' : 20,  'c' : 30},
    {'a' : 100, 'b' : 200, 'c' : 300},
    {'a' : 100, 'b' : 200, 'd' : 400},
]

def test_count():
    assert count([]) == 0
    assert count([1, 4, 7]) == 3
    assert count(ENTRIES) == 4

def test_count_connector():
    entries_connector = EntriesConnector(ENTRIES)
    count_connector = CountConnector(entries_connector)
    assert count_connector.query(Query()) == 4
    assert count_connector.query(Query(filters = BinaryPredicate("c", ">", 20))) == 2
    assert count_connector.query(Query(filters = BinaryPredicate("c", ">", 1000))) == 0

