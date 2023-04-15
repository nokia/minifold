#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query

def limit(entries: list, lim: int) -> list:
    """
    Implements the LIMITstatement for a list of minifold entries.

    Example:
        >>> where([{"a": 1, "b": 1}, {"a": 2, "b": 2}, {"a": 3, "b": 3}], 2)
        [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}]

    Args:
        entries (list): A list of minifold entries.
        lim (int): A positive integer, limiting the number of entries
            to return. Pass ``None`` if there is no limit.

    Returns:
        The kept entries.
    """
    return entries[:lim]

class LimitConnector(Connector):
    """
    The :py:class:`LimitConnector` class implements the LIMIT
    statement in a minifold pipeline.
    """
    def __init__(self, child, lim: int):
        """
        Constructor.

        Args:
            child (Connector): The child minifold :py:class:`Connector`
                instance.
            lim (int): A positive integer, limiting the number of entries
                to return. Pass ``None`` if there is no limit.
        """
        super().__init__()
        self.m_child = child
        self.m_lim = lim

    @property
    def child(self):
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`LimitConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return self.child.attributes(object)

    @property
    def limit(self) -> int:
        """
        Accessor to the limit size.

        Returns:
            The limit size or ``None`` (no limit).
        """
        return self.m_lim

    def query(self, q: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """
        super().query(q)
        return self.answer(
            q,
            limit(
                self.m_child.query(q),
                self.m_lim
            )
        )
