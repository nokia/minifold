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

from minifold.binary_predicate  import BinaryPredicate
from minifold.dblp              import DblpConnector
from minifold.query             import Query
from minifold.log               import Log

Log.enable_print = True

CONFERENCES = {"FORTE"}

FULLNAMES = [
    "Natalya Rozhnova",  # No trap here
    "Marc-Olivier Buob", # Composed firstname
    "Céline Comte",      # Accent
    "François Durand",   # Special characters
    "Ana Bušić",         # Special characters
]

DBLP_MAP_PID = {
    "Bartek Blaszczyszyn" : "88/4182",
    "Chung Shue Chen"     : "30/1446",
    "Giovanni Pau"        : "87/6423",
    "Fabien Schneider"    : "77/2750-1",
    "Xuan Zeng"           : "58/5418-2",
}

DBLP = DblpConnector(map_dblp_id = DBLP_MAP_PID)

def test_conference():
    for conference in CONFERENCES:
        entries = DBLP.query(Query(
            object  = "conference",
            filters = BinaryPredicate("conference", "==", conference)
        ))

def test_dblp_bibliography_without_pid():
    for fullname in FULLNAMES:
        entries = DBLP.query(Query(object = fullname))
        assert len(entries) > 0

def test_dblp_bibliography_with_pid():
    for fullname in DBLP_MAP_PID.keys():
        entries = DBLP.query(Query(object = fullname))
        assert len(entries) > 0

def test_dblp_publication():
    attributes = ["title", "authors", "year"]
    year       = 2016
    fullname   = "Marc-Olivier Buob"

    entries = DBLP.query(Query(
        object = "publication",
        attributes = attributes,
        filters = BinaryPredicate(
            BinaryPredicate("year", "==", year),
            "&&",
            BinaryPredicate("authors", "==", fullname)
        )
    ))
    assert len(entries) > 0
    for entry in entries:
        assert set(entry.keys()) == set(attributes)
        assert entry["year"] == year

def test_dblp_researcher():
    attributes = ["title", "authors", "year"]
    year       = 2008
    fullname   = "Marc-Olivier Buob"

    entries = DBLP.query(Query(
        object = "publication",
        attributes = attributes,
        filters = BinaryPredicate(
            BinaryPredicate("year", "==", year),
            "&&",
            BinaryPredicate("authors", "==", fullname)
        )
    ))
    assert len(entries) == 2
    assert len(entries[0]["authors"]) == 1
    assert len(entries[1]["authors"]) == 3

