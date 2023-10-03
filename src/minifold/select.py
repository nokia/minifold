#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query


def select(entries: list, attributes: list) -> list:
    """
    Implements the SELECT statement for a list of minifold entries.

    Example:
        >>> select([{"a": 1, "b": 2, "c": 3}, {"a": 10, "b": 20, "c": 30}], ["a", "b"])
        [{'a': 1, 'b': 2}, {'a': 10, 'b': 20}]

    Args:
        entries (list): A list of minifold entries.
        attributes (list): The selected keys.

    Returns:
        The input entries, restricted to the key of interest.
    """
    return [{k: entry[k] for k in attributes} for entry in entries]


class SelectConnector(Connector):
    """
    The :py:class:`SelectConnector` class implements the SELECT
    statement in a minifold pipeline.
    """
    def __init__(self, child: Connector, attributes: list):
        """
        Constructor.

        Args:
            child (Connector): The child minifold :py:class:`Connector`
                instance.
            attributes (list): The selected keys.
        """
        super().__init__()
        self.m_child = child
        self.m_attributes = attributes

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`SelectConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return set(self.m_attributes) & self.m_child.attributes(object)

    @property
    def child(self):
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    def query(self, query: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """
        super().query(query)
        q = query.copy()
        q.attributes = [
            attribute
            for attribute in q.attributes
            if attribute in self.m_attributes
        ]
        return self.answer(
            query,
            select(
                self.m_child.query(q),
                self.m_attributes
            )
        )
