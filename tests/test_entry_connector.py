#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pprint                         import pprint

from minifold.binary_predicate      import BinaryPredicate
from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query, ACTION_READ

if __name__ == '__main__':
    entries = [
        {'a' : 1,   'b' : 2,   'c' : 3},
        {'a' : 10,  'b' : 20,  'c' : 30},
        {'a' : 100, 'b' : 200, 'c' : 300},
        {'a' : 100, 'b' : 200, 'd' : 400},
    ]

    print("Entries:")
    pprint(entries)

    entries_connector = EntriesConnector(entries)
    q = Query(
        action = ACTION_READ,
        object = "",
        attributes = ["a", "c", "d"],
        filters = BinaryPredicate(BinaryPredicate("a", "<=", 100), "&&", BinaryPredicate("b", ">", 20))
    )
    print("Query: %s" % q)

    print("Result:")
    pprint(entries_connector.query(q))

    sys.exit(0)
