#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from pprint                         import pprint
from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query, ACTION_READ
from minifold.sort_by               import sort_by, SortByConnector
from minifold.values_from_dict      import ValuesFromDictFonctor

if __name__ == '__main__':

    entries = [
        {"a" : 1,    "b" : 200, "c" : 31},
        {"a" : 1,    "b" : 250, "c" : 3},
        {"a" : 10,   "b" : 200, "c" : 300},
        {"a" : 100,  "b" : 2,   "c" : 30},
    ]

    for k in ["a", "b", "c", ["a", "b"], ["b", "a"]]:
        print("sort by %s" % k)
        pprint(sort_by(k if isinstance(k, list) else [k], entries))
        print("reversed sort by %s" % k)
        pprint(sort_by(k if isinstance(k, list) else [k], entries, True))

    print("connector sort by b, a")
    sort_by_connector = SortByConnector(
        ["b", "a"],
        EntriesConnector(entries)
    )

    pprint(sort_by_connector.query(Query(
        action = ACTION_READ,
        object = "",
        attributes = [],
    )))

    sys.exit(0)
