#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query

def where(entries: list, f: callable) -> list:
    """
    Implements the WHERE statement for a list of minifold entries.

    Example:
        >>> where([{"a": 1, "b": 1}, {"a": 2, "b": 2}, {"a": 3, "b": 3}], lambda e: e["a"] <= 2)
        [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}]

    Args:
        entries (list): A list of minifold entries.
        f (callable): A function such that ``f(entry)`` returns
            ``True`` if ``entry`` must be kept,
            ``False`` otherwise.

    Returns:
        The kept entries.
    """
    return [entry for entry in entries if f(entry)]

class WhereConnector(Connector):
    """
    The :py:class:`WhereConnector` class implements the WHERE
    statement in a minifold pipeline.
    """
    def __init__(self, child: Connector, keep_if: callable):
        """
        Constructor.

        Args:
            child (Connector): The child minifold :py:class:`Connector`
                instance.
            keep_if (callable): A function such that ``f(entry)`` returns
                ``True`` if ``entry`` must be kept,
                ``False`` otherwise.
        """
        super().__init__()
        self.m_child = child
        self.m_keep_if = keep_if

    @property
    def child(self):
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    def attributes(self, object :str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`WhereConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return self.child.attributes(object)

    @property
    def keep_if(self):
        """
        Accessor to the filtering function used by this
        :py:class:`WhereConnector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_keep_if

    def query(self, q :Query) -> list:
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
            where(
                self.m_child.query(q),
                self.m_keep_if
            )
        )
