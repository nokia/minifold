#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .hash import to_hashable
from .query import Query
from .values_from_dict import ValuesFromDictFonctor

def group_by_impl(functor: ValuesFromDictFonctor, entries: list) -> dict:
    """
    Implementation details of :func:`group_by`.

    Args:
        functor (ValuesFromDictFonctor): The functor allowing to extract
            the values used to form the aggregates.
        entries (list): A list of minifold entries.

    Returns:
        A dictionary where each key identifies an aggregate and is mapped
        to the corresponding entries.
    """
    ret = dict()
    for entry in entries:
        key = functor(entry)
        if len(key) == 1:
            (key,) = key
        key = to_hashable(key)
        if key not in ret.keys():
            ret[key] = list()
        ret[key].append(entry)
    return ret

def group_by(attributes: list, entries: list) -> dict:
    """
    Implements the GROUP BY statement for a list of minifold entries.

    Args:
        attributes (list): The list of entry keys used to form the aggregates.
        entries (list): A list of minifold entries.

    Returns:
        A dictionary where each key identifies an aggregate and is mapped
        to the corresponding entries.
    """
    functor = ValuesFromDictFonctor(attributes)
    return group_by_impl(functor, entries)

class GroupByConnector(Connector):
    """
    The :py:class:`GroupByConnector` class implements the GROUP BY
    statement in a minifold pipeline.
    """
    def __init__(self, attributes: list, child: Connector):
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
    def child(self) -> Connector:
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`GroupByConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return set(self.m_functor.attributes)

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
            group_by_impl(
                self.m_functor,
                self.m_child.query(q)
            )
        )

    def __str__(self) -> str:
        """
        Returns the string representation of this
        :py:class:`GroupByConnector` instance

        Returns:
            The string representation of this
            :py:class:`GroupByConnector` instance
        """
        return "GROUP BY %s" % ", ".join(self.m_functor.attributes)
