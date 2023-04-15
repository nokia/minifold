#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from itertools import chain
from .connector import Connector
from .query import Query, ACTION_READ

def union_gen(list_entries: list) -> iter:
    """
    Iterator over a list of list of dicts.

    Args:
        list_entries: A list of lists of dicts.

    Returns:
        The resulting generator.
    """
    return chain(*list_entries)

def union(list_entries: list) -> list:
    """
    Make the union of several lists of entries.
    Use minifold.distinct() to remove duplicates.

    Args:
        list_entries: A list of lists of dicts.

    Returns:
        The resulting list of dicts.
    """
    return [entry for entry in union_gen(list_entries)]

class UnionConnector(Connector):
    """
    The :py:class:`UnionConnector` class implements the UNION
    statement in a minifold pipeline.
    """
    def __init__(self, children: list):
        """
        Constructor.

        Args:
            child (Connector): The list of children
                minifold :py:class:`Connector` instances.
        """

        super().__init__()
        self.children = children

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`WhereConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        attrs = set()
        for child in self.children:
            try:
                attrs |= child.attributes(object)
            except:
                pass
        return attrs

    def query(self, query :Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """
        super().query(query)
        if query.action != ACTION_READ:
            raise ValueError("Invalid action in query %s" % query)
        return union([child.query(query) for child in self.children])
