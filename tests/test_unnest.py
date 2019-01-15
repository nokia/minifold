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

from minifold.entries_connector import EntriesConnector
from minifold.unnest            import UnnestConnector, unnest

ENTRIES = [
    {'c' : [3,   3.1,   3.2]},
    {'c' : [30,  30.1]},
]

MAP_UNNEST = {
    "c" : "C",
}

def test_unnest():
    entries = unnest(MAP_UNNEST, ENTRIES)
    assert entries == [
        {"C" : 3},
        {"C" : 3.1},
        {"C" : 3.2},
        {"C" : 30},
        {"C" : 30.1},
    ]
