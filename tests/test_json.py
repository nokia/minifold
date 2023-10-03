#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.binary_predicate import BinaryPredicate
from minifold.json import JsonConnector
from minifold.query import Query


JSON_CONTENT = """
[
    {
        "firstname" : "John",
        "lastname"  : "Doe"
    }, {
        "firstname" : "Jane",
        "lastname"  : "Doe"
    }, {
        "firstname" : "John",
        "lastname"  : "Connor"
    }
]
"""


def test_json_select():
    connector = JsonConnector(JSON_CONTENT)
    firstnames = {
        entry["firstname"]
        for entry in connector.query(Query(attributes=["firstname"]))
    }
    assert firstnames == {"John", "Jane"}


def test_json_select_where():
    connector = JsonConnector(JSON_CONTENT)
    john_lastnames = {
        entry["lastname"]
        for entry in connector.query(
            Query(
                attributes=["lastname"],
                filters=BinaryPredicate("firstname", "==", "John")
            )
        )
    }
    assert john_lastnames == {"Doe", "Connor"}
