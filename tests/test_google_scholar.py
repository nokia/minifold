#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.binary_predicate  import BinaryPredicate
from minifold.query             import Query
from minifold.google_scholar    import GoogleScholarConnector

SCHOLAR = GoogleScholarConnector()

def test_google_scholar():
    entries = SCHOLAR.query(Query(
        filters = BinaryPredicate("author", "==", "Marc-Olivier Buob")
    ))
    assert len(entries) >= 9

def test_google_scholar_where_year():
    entries = SCHOLAR.query(Query(
        filters = BinaryPredicate(
            BinaryPredicate("author", "==", "Marc-Olivier Buob"),
            "&&",
            BinaryPredicate(
                BinaryPredicate("year", "<=", 2018),
                "&&",
                BinaryPredicate("year", ">=", 2016)
            )
        )
    ))
    assert len(entries) == 6

def test_google_scholar_limit():
    entries = SCHOLAR.query(Query(
        filters = BinaryPredicate("author", "==", "Marc-Olivier Buob"),
        limit = 2
    ))
    assert len(entries) == 2
