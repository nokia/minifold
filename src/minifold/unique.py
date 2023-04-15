#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .hash import to_hashable
from .query import Query
from .values_from_dict import ValuesFromDictFonctor

def unique_impl(functor :ValuesFromDictFonctor, entries :list) -> list:
    """
    Implementation details of :func:`unique`.

    Args:
        functor (ValuesFromDictFonctor): The functor allowing to extract
            the values used to form the aggregates.
        entries (list): A list of minifold entries.

    Returns:
        A dictionary where each entries are unique with respect to ``functor``.
    """
    ret = list()
    seen_keys = set()
    for entry in entries:
        key = functor(entry)
        if len(key) == 1:
            (key,) = key
        key = to_hashable(key)
        if key not in seen_keys:
            ret.append(entry)
            seen_keys.add(key)
    return ret

def unique(attributes :list, entries :list) -> list:
    """
    Implements the UNIQUE statement for a list of minifold entries.

    Args:
        attributes (list): The list of entry keys used to determine the uniqueness.
        entries (list): A list of minifold entries.

    Returns:
        The remaining entries once the UNIQUE filtering has been applied.
    """
    functor = ValuesFromDictFonctor(attributes)
    return unique_impl(functor, entries)

class UniqueConnector(Connector):
    """
    The :py:class:`UniqueConnector` class implements the GROUP BY
    statement in a minifold pipeline.
    """
    def __init__(self, attributes :list, child):
        """
        Constructor.

        Args:
            attributes (list): The list of entry keys used to form
                the aggregates.
            child (Connector): The child minifold :py:class:`Connector`
                instance.
        """
        super().__init__()
        self.m_functor = ValuesFromDictFonctor(attributes)
        self.m_child = child

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
        minifold entries exposed by this :py:class:`UniqueConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """

        return self.child.attributes(object)

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
            unique_impl(
                self.m_functor,
                self.m_child.query(q)
            )
        )

    def __str__(self) -> str:
        """
        Returns the string representation of this
        :py:class:`UniqueConnector` instance

        Returns:
            The string representation of this
            :py:class:`UniqueConnector` instance
        """
        return "DUP %s" % ", ".join(self.m_functor.attributes)
