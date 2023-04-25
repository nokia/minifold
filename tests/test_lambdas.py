#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.entries_connector import EntriesConnector
from minifold.query import Query
from minifold.lambdas import (
    LambdasConnector,
    find_lambda_dependencies,
    find_lambdas_dependencies
)

ENTRIES = [
    {"a": 1, "b": 2, "c": 3, "d": 4},
    {"a": 10, "b": 20, "c": 30, "d": 40},
    {"a": 100, "b": 200, "c": 300, "d": 400}
]

class StrictEntriesConnector(EntriesConnector):
    def __init__(self, entries):
        super().__init__(entries)
        self.last_queried_attributes = None

    def query(self, q :Query) -> list:
        assert set(q.attributes) <= self.attributes(None)
        self.last_queried_attributes = set(q.attributes)
        return super().query(q)

STRICT_CONNECTOR = StrictEntriesConnector(ENTRIES)

MAP_LAMBDAS = {
    "a2": lambda e: e["a"] ** 2,       # a^2
    "a3": lambda e: e["a"] * e["a2"],  # a^3
    "b2": lambda e: e["b"] ** 2,       # ...
    "b3": lambda e: e["b"] * e["b2"],
    "c2": lambda e: e["c"] ** 2,
    "c3": lambda e: e["c"] * e["c2"],
    "d": lambda e: e["d"] * 10
}

LAMBDAS_CONNECTOR = LambdasConnector(MAP_LAMBDAS, STRICT_CONNECTOR)

def check_keys(entries :list, expected_keys :set):
    for entry in entries:
        assert set(entry.keys()) == expected_keys

def test_find_lambda_dependencies():
    obtained = find_lambda_dependencies(MAP_LAMBDAS["a2"])
    assert obtained == {"a"}
    obtained = find_lambda_dependencies(MAP_LAMBDAS["a3"])
    assert obtained == {"a", "a2"}

def test_find_lambdas_dependencies():
    map_required_keys = find_lambdas_dependencies(MAP_LAMBDAS)
    expected = {
        "a2": {"a"},
        "a3": {"a", "a2"},
        "b2": {"b"},
        "b3": {"b", "b2"},
        "c2": {"c"},
        "c3": {"c", "c2"},
        "d": {"d"}
    }
    assert map_required_keys == expected

def test_lambdas_simple():
    attributes = {"a", "b", "c"}
    obtained = LAMBDAS_CONNECTOR.query(Query(attributes = attributes))
    check_keys(obtained, attributes)
    assert obtained == [
        {"a": 1, "b": 2, "c": 3},
        {"a": 10, "b": 20, "c": 30},
        {"a": 100, "b": 200, "c": 300}
    ]

def test_lambdas_all():
    attributes = {
        "a", "a2", "a3",
        "b", "b2", "b3",
        "c", "c2", "c3",
        "d"
    }

    obtained = LAMBDAS_CONNECTOR.query(Query())
    check_keys(obtained, attributes)
    assert STRICT_CONNECTOR.last_queried_attributes == set()

    obtained = LAMBDAS_CONNECTOR.query(Query(attributes = attributes))
    check_keys(obtained, attributes)
    assert STRICT_CONNECTOR.last_queried_attributes == {"a", "b", "c", "d"}

def test_lambdas_x2():
    attributes = {"a2", "b2", "c2"}
    obtained = LAMBDAS_CONNECTOR.query(Query(attributes = attributes))
    check_keys(obtained, attributes)

def test_lambdas_where():
    expected = [
        {
            "a": 10,
            "a2": 100,
            "a3": 1000,
            "b": 20,
            "b2": 400,
            "b3": 8000,
            "c": 30,
            "c2": 900,
            "c3": 27000,
            "d": 400,
        }
    ]

    obtained = LAMBDAS_CONNECTOR.query(Query(filters = lambda e: e["a"] == 10))
    assert obtained == expected

    obtained = LAMBDAS_CONNECTOR.query(Query(filters = lambda e: e["a2"] == 100))
    assert obtained == expected

def test_lambdas_select_where():
    expected = [
        {
            "a2": 100,
            "a3": 1000,
            "b": 20,
            "b2": 400,
        }
    ]

    obtained = LAMBDAS_CONNECTOR.query(Query(
        attributes = ["a2", "a3", "b", "b2"],
        filters = lambda e: e["a"] == 10
    ))
    assert obtained == expected

    obtained = LAMBDAS_CONNECTOR.query(Query(
        attributes = ["a2", "a3", "b", "b2"],
        filters = lambda e: e["a2"] == 100
    ))
    assert obtained == expected

def test_lambdas_attributes():
    obtained = LAMBDAS_CONNECTOR.attributes(None)
    expected = {
        "a", "a2", "a3",
        "b", "b2", "b3",
        "c", "c2", "c3",
        "d"
    }
    assert obtained == expected
