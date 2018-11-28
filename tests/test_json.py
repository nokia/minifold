#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"


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


