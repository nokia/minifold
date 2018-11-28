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

from minifold.entries_connector     import EntriesConnector
from minifold.query                 import Query, ACTION_READ
from minifold.group_by              import group_by, GroupByConnector
from minifold.values_from_dict      import ValuesFromDictFonctor

if __name__ == '__main__':

    entries = [
        {"a" : 1,    "b" : 200, "c" : 31},
        {"a" : 1,    "b" : 250, "c" : 3},
        {"a" : 10,   "b" : 200, "c" : 300},
        {"a" : 100,  "b" : 2,   "c" : 30},
    ]

    for k in ["a", "b", "c", ["a", "b"], ["b", "a"]]:
        print("group by %s" % k)
        pprint(group_by(k if isinstance(k, list) else [k], entries))

    print("connector group by b, a")
    group_by_connector = GroupByConnector(
        ["b", "a"],
        EntriesConnector(entries)
    )

    pprint(group_by_connector.query(Query(
        action = ACTION_READ,
        object = "",
        attributes = [],
    )))

    sys.exit(0)
