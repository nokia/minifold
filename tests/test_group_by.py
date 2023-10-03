#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.entries_connector import EntriesConnector
from minifold.query import Query, ACTION_READ
from minifold.group_by import group_by, GroupByConnector

ENTRIES = [
    {"a": 1, "b": 200, "c": 31},
    {"a": 1, "b": 250, "c": 3},
    {"a": 10, "b": 200, "c": 300},
    {"a": 100, "b": 2, "c": 30},
]


def test_group_by_a():
    # for k in ["a", "b", "c", ["a", "b"], ["b", "a"]]:
    aggregat = group_by("a", ENTRIES)
    assert len(aggregat[1]) == 2
    assert len(aggregat[10]) == 1
    assert len(aggregat[100]) == 1


def test_group_by_b():
    aggregat = group_by("b", ENTRIES)
    assert len(aggregat[2]) == 1
    assert len(aggregat[200]) == 2
    assert len(aggregat[250]) == 1
    assert len(aggregat) == 3


def test_group_by_c():
    aggregat = group_by("c", ENTRIES)
    assert len(aggregat[31]) == 1
    assert len(aggregat[3]) == 1
    assert len(aggregat[30]) == 1
    assert len(aggregat[300]) == 1
    assert len(aggregat) == 4


def test_group_by_ab():
    aggregat = group_by(("a", "b"), ENTRIES)
    assert len(aggregat[(1, 200)]) == 1
    assert len(aggregat[(1, 250)]) == 1
    assert len(aggregat[(10, 200)]) == 1
    assert len(aggregat[(100, 2)]) == 1
    assert len(aggregat) == 4


def test_group_by_ba():
    aggregat = group_by(("b", "a"), ENTRIES)
    assert len(aggregat[(200, 1)]) == 1
    assert len(aggregat[(250, 1)]) == 1
    assert len(aggregat[(200, 10)]) == 1
    assert len(aggregat[(2, 100)]) == 1
    assert len(aggregat) == 4


def test_group_by_connector():
    print("connector group by b, a")
    group_by_connector = GroupByConnector(
        ("b", "a"),
        EntriesConnector(ENTRIES)
    )

    assert len(group_by_connector.query(Query(
        action=ACTION_READ,
        object="",
        attributes=[],
    ))) == 4
