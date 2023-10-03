#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.binary_predicate import BinaryPredicate
from minifold.query import Query
from minifold.google_scholar import GoogleScholarConnector

SCHOLAR = GoogleScholarConnector()


def test_google_scholar():
    try:
        entries = SCHOLAR.query(Query(
            filters=BinaryPredicate("authors", "CONTAINS", "Marc-Olivier Buob")
        ))
        assert len(entries) >= 9
    except RuntimeError:
        pass


def test_google_scholar_where_year():
    try:
        entries = SCHOLAR.query(Query(
            filters=BinaryPredicate(
                BinaryPredicate("authors", "CONTAINS", "Marc-Olivier Buob"),
                "&&",
                BinaryPredicate(
                    BinaryPredicate("year", "<=", 2018),
                    "&&",
                    BinaryPredicate("year", ">=", 2016)
                )
            )
        ))
        assert len(entries) == 5
    except RuntimeError:
        pass


def test_google_scholar_limit():
    try:
        entries = SCHOLAR.query(Query(
            filters=BinaryPredicate("authors", "CONTAINS", "Marc-Olivier Buob"),
            limit=2
        ))
        assert len(entries) == 2
    except RuntimeError:
        pass
