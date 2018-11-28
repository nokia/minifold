#!/usr/bin/env python3
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

from minifold.binary_predicate      import BinaryPredicate
from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query, ACTION_READ
from minifold.select                import select, SelectConnector

if __name__ == '__main__':
    entries = [
        {'a' : 1,   'b' : 2,   'c' : 3},
        {'a' : 10,  'b' : 20,  'c' : 30},
        {'a' : 100, 'b' : 200, 'c' : 300}
    ]

    attributes = ["a", "c"]

    # Method 1: filter with function
    pprint(select(entries, attributes))

    # Method 2: if the connector supports projection, pass the filter in the query
    entries_connector = EntriesConnector(entries)
    pprint(entries_connector.query(Query(
        action = ACTION_READ,
        object = "",
        attributes = attributes
    )))

    # Method 3: if not, you could always project afterwards
    select_connector = SelectConnector(entries_connector, attributes)
    pprint(select_connector.query(Query(
        action = ACTION_READ,
        object = "",
        attributes = [],
    )))

    sys.exit(0)
