#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query, ACTION_READ

def count_gen(gen: iter) -> int:
    """
    Count the number of elements listed by a generator.

    Args:
        gen (iter): A generator.

    Returns:
        The number of elements listed by a generator.
    """
    n = 0
    for _ in gen:
        n += 1
    return n

def count(entries: list) -> int:
    """
    Count the number of entries.

    Args:
        entries (list): A list of entries.

    Returns:
        The number of element in entries.
    """
    return len(entries)

class CountConnector(Connector):
    """
    The :py:class:`CountConnector` class is used to implement the COUNT
    SQL operator in a minifold query plan. As it is one of the rare
    connector returning an integer (instead of a list of entries) this
    is often the root connector in the tree modeling the minifold query plan.
    """
    def __init__(self, child :Connector):
        """
        Constructor.

        Args:
            child (Connector): The child :py:class:`Connector` instance.
        """
        super().__init__()
        self.m_child = child

    def query(self, query: Query) -> int:
        """
        Handles a minifold query.

        Args:
            query (Query): The handled :py:class:`Query` instance.

        Raises:
            ValueError: if ``query.action != ACTION_READ``.

        Returns:
            The number of entries matched by this :py:class:`Query`.
        """
        super().query(query)
        if query.action != ACTION_READ:
            raise ValueError("Invalid action in query %s" % query)
        return count(self.m_child.query(query))
