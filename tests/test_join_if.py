#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.entries_connector import EntriesConnector
from minifold.join_if import (
    JoinIfConnector,
    INNER_JOIN, LEFT_JOIN, RIGHT_JOIN, FULL_OUTER_JOIN,
    inner_join_if, left_join_if, right_join_if, full_outer_join_if
)
from minifold.query import Query

ENTRIES1 = [
    {"k1": "left", "k12": "only1"},
    {"k1": "match1", "k12": "match"}
]

ENTRIES2 = [
    {"k2": "right",  "k12": "only2"},
    {"k2": "match2", "k12": "match"}
]


def test_left_join():
    obtained = left_join_if(
        ENTRIES1, ENTRIES2,
        lambda l, r: l["k12"] == r["k12"]
    )
    expected = [
        {"k1": "left", "k12": "only1", "k2": None},
        {"k1": "match1", "k12": "match", "k2": "match2"}
    ]
    assert obtained == expected


def test_right_join():
    obtained = right_join_if(
        ENTRIES1, ENTRIES2,
        lambda l, r: l["k12"] == r["k12"]
    )
    expected = [
        {"k1": None, "k12": "only2", "k2": "right"},
        {"k1": "match1", "k12": "match", "k2": "match2"}
    ]
    assert obtained == expected


def test_full_outer_join():
    obtained = full_outer_join_if(
        ENTRIES1, ENTRIES2,
        lambda l, r: l["k12"] == r["k12"]
    )
    expected = [
        {"k1": "left", "k12": "only1", "k2": None},
        {"k1": "match1", "k12": "match", "k2": "match2"},
        {"k1": None, "k12": "only2", "k2": "right"}
    ]
    assert obtained == expected


def test_inner_join():
    obtained = inner_join_if(
        ENTRIES1, ENTRIES2,
        lambda l, r: l["k12"] == r["k12"]
    )
    expected = [
        {"k1": "match1", "k12": "match", "k2": "match2"}
    ]
    assert obtained == expected


def test_join_if_connector():
    expected = {
        INNER_JOIN: 1,
        LEFT_JOIN: 2,
        RIGHT_JOIN: 2,
        FULL_OUTER_JOIN: 3
    }
    for mode in expected.keys():
        connector = JoinIfConnector(
            EntriesConnector(ENTRIES1),
            EntriesConnector(ENTRIES2),
            lambda l, r: l["k12"] == r["k12"],
            mode
        )
        assert len(connector.query(Query())) == expected[mode]
