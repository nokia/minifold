#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.entries_connector import EntriesConnector
from minifold.natural_join import NaturalJoinConnector, natural_join
from minifold.query import Query

RESEARCHERS = [
    {"institution_id": 5, "name": "Name5"},
    {"institution_id": 5, "name": "Name5_"},
    {"institution_id": 2, "name": "Name2"},
    {"institution_id": 4, "name": "Name4"},
]

INSTITUTIONS = [
    {"institution_id": 1, "institution": "Institut1"},
    {"institution_id": 2, "institution": "Institut2"},
    {"institution_id": 3, "institution": "Institut3"},
    {"institution_id": 4, "institution": "Institut4"},
    {"institution_id": 5, "institution": "Institut5"},
]

EXPECTED = [
    {"institution": "Institut5", "institution_id": 5, "name": "Name5"},
    {"institution": "Institut5", "institution_id": 5, "name": "Name5_"},
    {"institution": "Institut2", "institution_id": 2, "name": "Name2"},
    {"institution": "Institut4", "institution_id": 4, "name": "Name4"}
]


def test_natural_join():
    obtained = natural_join(RESEARCHERS, INSTITUTIONS)
    assert obtained == EXPECTED


def test_natural_join_connector():
    connector = NaturalJoinConnector(
        EntriesConnector(RESEARCHERS),
        EntriesConnector(INSTITUTIONS)
    )

    obtained = connector.query(
        Query(
            attributes=["name", "institution_id", "institution"]
        )
    )

    assert obtained == EXPECTED
