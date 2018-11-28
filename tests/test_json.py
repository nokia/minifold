#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from minifold.binary_predicate  import BinaryPredicate
from minifold.json              import JsonConnector
from minifold.query             import Query

json_content = """
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

connector = JsonConnector(json_content)

firstnames = {
    entry["firstname"] \
    for entry in connector.query(Query(attributes = ["firstname"]))
}
assert firstnames == {"John", "Jane"}

john_lastnames = {
    entry["lastname"] \
    for entry in connector.query(
        Query(
            attributes = ["lastname"],
            filters    = BinaryPredicate("firstname", "==", "John")
        )
    )
}
assert john_lastnames == {"Doe", "Connor"}


