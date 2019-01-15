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
    "Salah Eddine Elayoubi" : "salah-eddine-elayoubi",
    "François Durand"       : "fradurand",
    "Chung Shue Chen"       : "chung-shue-chen",
    "Dario Rossi"           : "rossi-dario",
}

HAL = HalConnector(map_hal_id = HAL_MAP_ID)

def test_hal_bibliography():
    try:
        for fullname in FULLNAMES:
            entries = HAL.query(Query(object = fullname))
            assert len(entries) > 0
    except urllib3.exceptions.MaxRetryError:
        assert False, "Network unavailable"

def test_hal_hid():
    try:
        for fullname in HAL_MAP_ID.keys():
            entries = HAL.query(Query(object = fullname))
            assert len(entries) > 0
    except urllib3.exceptions.MaxRetryError:
        assert False, "Network unavailable"

def test_lincs_laboratory():
    fullname = "Marc-Olivier Buob"
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
    fullname = "Marc-Olivier Buob"
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

#TODO test the others HAL objects
#TODO test operators
