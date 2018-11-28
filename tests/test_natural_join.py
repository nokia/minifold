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
from minifold.natural_join          import NaturalJoinConnector, natural_join
from minifold.query                 import Query, ACTION_READ
from minifold.rename                import rename
from minifold.strings               import to_canonic_string

if __name__ == '__main__':

    researchers = [
        {"institution_id" : 5, "name" : "Fabien Mathieu"},
        {"institution_id" : 5, "name" : "Marc-Olivier Buob"},
        {"institution_id" : 2, "name" : "Serge Fdida"},
        {"institution_id" : 4, "name" : "Jordan Augé"},
    ]

    institutions = [
        {"institution_id" : 1, "institution" : "TPT"},
        {"institution_id" : 2, "institution" : "UPMC"},
        {"institution_id" : 3, "institution" : "INRIA"},
        {"institution_id" : 4, "institution" : "SystemX"},
        {"institution_id" : 5, "institution" : "Nokia"},
    ]

    pprint(natural_join(researchers, institutions))

    connector = NaturalJoinConnector(
        EntriesConnector(researchers),
        EntriesConnector(institutions)
    )

    q = Query(
        action     = ACTION_READ,
        object     = "",
        attributes = ["name", "institution_id", "institution"]
    )

    pprint(connector.query(q))

    sys.exit(0)

