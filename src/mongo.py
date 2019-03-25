#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Dylan Sellar"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from minifold.binary_predicate    import BinaryPredicate
from minifold.connector           import Connector
from minifold.query               import Query, ACTION_READ
from minifold.where               import where
from pymongo                      import MongoClient

class MongoConnector(Connector):
    def __init__(self, mongo_url :str, db_name :str):
        self.client = self.connect(mongo_url)
        self.db_name = db_name
        self.use_database(db_name)

    def connect(self, mongo_url :str) -> MongoClient:
        return MongoClient(mongo_url)

    def use_database(self, db_name :str):
        self.db = self.client[db_name]

    def attributes(self, obj :str = None) -> set:
        return set()

    def query(self, query :Query) -> list:
        super().query(query)
        ret = list()
        assert self.db
        if query.action == ACTION_READ:
            ret = list(
                self.db[query.object].find(
                    {},
                    {k : 1 for attr in query.attributes} if query.attributes else None
                )
                    .limit(query.limit if query.limit else 0)
                    .skip(query.offset if query.offset else 0)
            )
            if not query.filters:
                pass
            elif isinstance(query.filters, BinaryPredicate):
                raise RuntimeError("MongoConnector::query: Not yet implemented")
            else:
                return where(ret, query.filters)
        else:
            raise RuntimeError("MongoConnector::query: Unable to query")
        return self.answer(query, ret)
