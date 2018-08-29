#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
