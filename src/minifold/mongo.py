#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .binary_predicate    import BinaryPredicate
from .connector           import Connector
from .query               import Query, ACTION_READ
from .where               import where

try:
    from pymongo import MongoClient
except ImportError as e:
    from .log import Log
    Log.warning(
        "Please install pymongo.\n"
        "  APT: sudo apt install python3-pymongo\n"
        "  PIP: sudo pip3 install --upgrade pymongo\n"
    )
    raise e

class MongoConnector(Connector):
    """
    The :py:class:`MongoConnector` is a minifold gateway allowing
    to manipulate data stored in a Mongo database.
    """
    def __init__(self, mongo_url: str, db_name: str):
        """
        Constructor.

        Args:
            mongo_url (str): The URL of the mongo database.
            db_name (str): The name of the queried database.
        """
        self.client = self.connect(mongo_url)
        self.db_name = db_name
        self.use_database(db_name)

    def connect(self, mongo_url: str) -> MongoClient:
        """
        Connects to a Mongo database.

        Args:
            mongo_url (str): The URL of the mongo database.

        Returns:
            The corresponding :py:class`MongoClient` instance.
        """
        return MongoClient(mongo_url)

    def use_database(self, db_name: str):
        """
        Selects the active database.

        Args:
            db_name (str): The name of the queried database.
        """
        self.db = self.client[db_name]

    def attributes(self, obj: str = None) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`MongoConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """

        return set()

    def query(self, query: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """
        super().query(query)
        ret = list()
        assert self.db
        if query.action == ACTION_READ:
            ret = list(
                self.db[query.object].find(
                    {},
                    {attr:  1 for attr in query.attributes} if query.attributes else None
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
