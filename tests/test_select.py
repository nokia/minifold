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

import sys
from pprint                         import pprint

from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query
from minifold.select                import select, SelectConnector

ENTRIES = [
    {"a" : 1,   "b" : 2,   "c" : 3},
    {"a" : 10,  "b" : 20,  "c" : 30},
    {"a" : 100, "b" : 200, "c" : 300}
]

ATTRIBUTES = ["a", "c"]

EXPECTED = [
    {"a" : 1,   "c" : 3},
    {"a" : 10,  "c" : 30},
    {"a" : 100, "c" : 300}
]

def test_select():
    obtained = select(ENTRIES, ATTRIBUTES)
    assert obtained == EXPECTED

def test_select_on_entries_connector():
    entries_connector = EntriesConnector(ENTRIES)
    obtained = entries_connector.query(
        Query(
            attributes = ATTRIBUTES
        )
    )
    assert obtained == EXPECTED

def test_select_connector_alters_query():
    entries_connector = EntriesConnector(ENTRIES)
    select_connector = SelectConnector(entries_connector, ATTRIBUTES)
    obtained = select_connector.query(
        Query(
            attributes = []
        )
    )
    assert obtained == EXPECTED
