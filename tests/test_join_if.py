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
from minifold.join_if               import INNER_JOIN, LEFT_JOIN, RIGHT_JOIN, FULL_OUTER_JOIN, left_join_if, right_join_if, join_mode_to_string, JoinIfConnector
from minifold.query                 import Query, ACTION_READ
from minifold.strings               import to_canonic_string

if __name__ == '__main__':
    # This example shows how to perform usual SQL join using arbitrary condition.
    # Note that by default, *join* functions and *Join*Connector pair one left entry with at most one right entry.
    # To disable this, just pass as parameter match_once = False to the connector (resp. function)

    entries1 = [
        {"author1" : "Sébastien", "title1" : "seb1"},
        {"author1" : "Sebastien", "title1" : "seb2"},
        {"author1" : "Francois",  "title1" : "fra1"},
        {"author1" : "Francois",  "title1" : "fra2"},
        {"author1" : "Left",      "title1" : "lef1"},
        {"author1" : "Left",      "title1" : "lef2"},
    ]

    entries2 = [
        {"author2" : "sebastien", "title2" : "seb1"},
        {"author2" : "SEBASTIEN", "title2" : "SEB2"},
        {"author2" : "françois",  "title2" : "fra1"},
        {"author2" : "Francois",  "title2" : "frä2"},
        {"author2" : "Right",     "title2" : "rig1"},
        {"author2" : "Right",     "title2" : "rig2"},
    ]

    pprint(entries1)
    pprint(entries2)

    # Test each join mode (connector mode)
    for mode in [INNER_JOIN, LEFT_JOIN, RIGHT_JOIN]:
        print("-" * 80)
        print("%s" % join_mode_to_string(mode))
        connector = JoinIfConnector(
            EntriesConnector(entries1),
            EntriesConnector(entries2),
            lambda l, r: \
                (to_canonic_string(l["author1"]) == to_canonic_string(r["author2"])) and \
                (to_canonic_string(l["title1"])  == to_canonic_string(r["title2"])),
            mode
        )

        pprint(connector.query(Query(
            action = ACTION_READ,
            object = "",
            attributes = ["title1", "title2", "author1", "author2"]
        )))

    print("-" * 80)

    # entries1 - entries2
    entries_in1_notin2 = [entry for entry in left_join_if(
        entries1,
        entries2,
        lambda l, r: \
            (to_canonic_string(l["author1"]) == to_canonic_string(r["author2"])) and \
            (to_canonic_string(l["title1"])  == to_canonic_string(r["title2"]))
    ) if entry["title2"] == None]

    print("entries1 - entries2 = %s" % entries_in1_notin2)

    # entries2 - entries1
    entries_notin1_in2 = [entry for entry in right_join_if(
        entries1,
        entries2,
        lambda l, r: \
            (to_canonic_string(l["author1"]) == to_canonic_string(r["author2"])) and \
            (to_canonic_string(l["title1"])  == to_canonic_string(r["title2"]))
    ) if entry["title1"] == None]

    print("entries2 - entries1 = %s" % entries_notin1_in2)


    sys.exit(0)

