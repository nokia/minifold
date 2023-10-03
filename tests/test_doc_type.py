#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.doc_type import DocType


def test_sort():
    hdr = DocType.HDR
    book = DocType.BOOKS_AND_THESES
    assert sorted([hdr, book]) == [book, hdr]


def test_dblp():
    from minifold.dblp import DblpConnector
    for s in [
        "conference and workshop papers",
        "conference or workshop",
        "journal articles",
        "informal publications",
        "books and theses",
        "editorship"
    ]:
        assert DblpConnector.to_doc_type(s) != DocType.UNKNOWN


def test_hal():
    from minifold.hal import HalConnector
    for s in ["art", "comm", "report", "hdr", "couv", "patent"]:
        assert HalConnector.to_doc_type(s) != DocType.UNKNOWN
