#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pprint                         import pprint

from minifold.binary_predicate      import BinaryPredicate
from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query, ACTION_READ
from minifold.where                 import where, WhereConnector

if __name__ == '__main__':
    entries = [
        {'a' : 1,   'b' : 2,   'c' : 3},
        {'a' : 10,  'b' : 20,  'c' : 30},
        {'a' : 100, 'b' : 200, 'c' : 300}
    ]

    # Method 1: filter with function
    keep_if = lambda entry: entry['a'] <= 10 and entry["c"] > 0
    pprint(where(entries, keep_if))

    # Method 2: if the connector supports filtering, pass the filter in the query
    entries_connector = EntriesConnector(entries)
    pprint(entries_connector.query(Query(
        action = ACTION_READ,
        object = "",
        attributes = [],
        filters = BinaryPredicate(BinaryPredicate("a", "<=", 10), "&&", BinaryPredicate("c", ">", 0))
    )))

    # Method 3: if not, you could always filter afterwards
    where_connector = WhereConnector(entries_connector, keep_if)
    pprint(where_connector.query(Query(
        action = ACTION_READ,
        object = "",
        attributes = [],
    )))

    sys.exit(0)
