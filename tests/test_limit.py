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
from minifold.limit                 import LimitConnector, limit

ENTRIES = [
    {'a' : 1,   'b' : 2,   'c' : 3},
    {'a' : 10,  'b' : 20,  'c' : 30},
    {'a' : 100, 'b' : 200, 'c' : 300}
]

EXPECTED = [
    {'a' : 1,   'b' : 2,   'c' : 3},
    {'a' : 10,  'b' : 20,  'c' : 30}
]

def test_limit():
    obtained = limit(ENTRIES, 2)
    assert obtained == EXPECTED

def test_limit_connector():
    entries_connector = EntriesConnector(ENTRIES)
    limit_connector = LimitConnector(entries_connector, 2)
    obtained = limit_connector.query(
        Query()
    )
    assert obtained == EXPECTED

