#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.entries_connector import EntriesConnector
from minifold.query import Query
from minifold.unique import unique, UniqueConnector


ENTRIES = [
    {"a": 1, "b": 200, "c": 31},
    {"a": 1, "b": 200, "c": 3},
    {"a": 10, "b": 200, "c": 300},
    {"a": 100, "b": 2, "c": 30}
]


def test_unique():
    expected = {
        "a": [
            {"a": 1, "b": 200, "c": 31},
            {"a": 10, "b": 200, "c": 300},
            {"a": 100, "b": 2, "c": 30}
        ],
        "b": [
            {"a": 1, "b": 200, "c": 31},
            {"a": 100, "b": 2, "c": 30}
        ],
        "c": [
            {"a": 1, "b": 200, "c": 31},
            {"a": 1, "b": 200, "c": 3},
            {"a": 10, "b": 200, "c": 300},
            {"a": 100, "b": 2, "c": 30}
        ],
        ("a", "b"): [
            {"a": 1, "b": 200, "c": 31},
            {"a": 10, "b": 200, "c": 300},
            {"a": 100, "b": 2, "c": 30}
        ],
        ("b", "a"): [
            {"a": 1, "b": 200, "c": 31},
            {"a": 10, "b": 200, "c": 300},
            {"a": 100, "b": 2, "c": 30}
        ]
    }
    for k in ["a", "b", "c", ("a", "b"), ("b", "a")]:
        obtained = unique(k if isinstance(k, tuple) else [k], ENTRIES)
        assert obtained == expected[k]


def test_unique_connector():
    unique_connector = UniqueConnector(
        ["a"],
        EntriesConnector(ENTRIES)
    )

    obtained = unique_connector.query(Query())
    expected = [
        {"a": 1, "b": 200, "c": 31},
        {"a": 10, "b": 200, "c": 300},
        {"a": 100, "b": 2, "c": 30}
    ]
    assert obtained == expected
