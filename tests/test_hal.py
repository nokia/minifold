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

import urllib3

from minifold.binary_predicate  import BinaryPredicate
from minifold.hal               import HAL_ALIASES, HalConnector
from minifold.log               import Log
from minifold.query             import Query
from minifold.rename            import RenameConnector

Log.enable_print = True

FULLNAMES = [
    "Natalya Rozhnova",  # No trap here
    "Marc-Olivier Buob", # Composed firstname
    "Céline Comte",      # Accent
    "François Durand",   # Special characters
    "Ana Bušić",         # Special characters
]

HAL_MAP_ID = {
    "François Durand" : "fradurand",
    "Chung Shue Chen" : "chung-shue-chen",
    "Dario Rossi"     : "rossi-dario",
}

HAL = HalConnector(map_hal_id = HAL_MAP_ID)
DEFAULT_ATTRIBUTES = ["title_s", "authFullName_s", "producedDateY_i", "uri_s"]

def test_hal_predicate_equals():
    p1 = BinaryPredicate("authFullName_s", "==", "Natalya Rozhnova")
    obtained = HAL.binary_predicate_to_hal(p1)
    expected = "authFullName_s:(%22Natalya%20Rozhnova%22)"
    assert obtained == expected

def test_hal_predicate_in():
    p2 = BinaryPredicate("producedDateY_i", "IN", (2015, 2017))
    obtained = HAL.binary_predicate_to_hal(p2)
    expected = "producedDateY_i:[2015%20TO%202017]"
    assert obtained == expected

def test_hal_predicate_and():
    p1 = BinaryPredicate("authFullName_s", "==", "Natalya Rozhnova")
    p2 = BinaryPredicate("producedDateY_i", "IN", (2015, 2017))
    p3 = BinaryPredicate(p1, "&&", p2)
    obtained = HAL.binary_predicate_to_hal(p3)
    expected = "authFullName_s:(%22Natalya%20Rozhnova%22)&fq=producedDateY_i:[2015%20TO%202017]"
    assert obtained == expected

def test_string_to_hal():
    assert HAL.string_to_hal("Natalya Rozhnova") == "%22Natalya%20Rozhnova%22"
    assert HAL.string_to_hal("Marc-Olivier Buob") == "%22Marc-Olivier%20Buob%22"
    assert HAL.string_to_hal("Céline Comte") == "%22C%C3%A9line%20Comte%22"

def test_hal_query():
    year = 2016
    fullname = "Natalya Rozhnova"
    query = Query(
        object     = "publication",
        attributes = DEFAULT_ATTRIBUTES,
        filters    = \
            BinaryPredicate(
                BinaryPredicate("authFullName_s", "==", fullname),
                "&&",
                BinaryPredicate("producedDateY_i", "IN", (year - 1, year + 1))
            )
    )
    obtained = HAL.query_to_hal(query)
    expected = "https://api.archives-ouvertes.fr/search/?q=*:*&fl=title_s,authFullName_s,producedDateY_i,uri_s&fq=authFullName_s:(%22Natalya%20Rozhnova%22)&fq=producedDateY_i:[2015%20TO%202017]&rows=2000&sort=submittedDate_tdate+desc&wt=json"
    assert obtained == expected

def test_hal_author_bibliography():
    try:
        for fullname in FULLNAMES:
            q = Query(attributes = ["title_s"], object = fullname)
            entries = HAL.query(q)
            assert len(entries) > 0
            print("%s: success" % fullname)
    except urllib3.exceptions.MaxRetryError:
        assert False, "Network unavailable"

def test_hal_hid():
    try:
        for fullname in HAL_MAP_ID.keys():
            entries = HAL.query(
                Query(
                    attributes = DEFAULT_ATTRIBUTES,
                    object = fullname
                )
            )
            assert len(entries) > 0, "Test failed for %s" % fullname
    except urllib3.exceptions.MaxRetryError:
        assert False, "Network unavailable"

def test_lincs_laboratory():
    year = 2016
    attributes = ["authFullName_s", "title_s", "producedDateY_i"]

    entries = HAL.query(Query(
        object     = "lincs",
        attributes = attributes,
        filters    = BinaryPredicate("producedDateY_i", "==" , year)
    ))

    assert len(entries) > 0
    for entry in entries:
        assert set(entry.keys()) == set(attributes)
        assert entry["producedDateY_i"] == year

def test_lincs_laboratory_with_aliases():
    hal_with_aliases = RenameConnector(HAL_ALIASES, HAL)
    year = 2016
    attributes = ["authors", "title", "year"]

    entries = hal_with_aliases.query(Query(
        object     = "lincs",
        attributes = attributes,
        filters    = BinaryPredicate("year", "==" , year)
    ))

    assert len(entries) > 0
    for entry in entries:
        assert set(entry.keys()) == set(attributes)
        assert entry["year"] == year

