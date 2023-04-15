#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query
from .values_from_dict import ValuesFromDictFonctor

def sort_by_impl(functor: ValuesFromDictFonctor, entries: list, desc: bool = True) -> list:
    """
    Implementation details of :func:`sort_by`.

    Args:
        functor (ValuesFromDictFonctor): The functor allowing to extract
            the values used to sort the entries.
        entries (list): A list of minifold entries.
        desc (bool): Pass ``True`` to sort by ascending order,
            ``False`` otherwise.

    Returns:
        The sorted entries, with respect to ``functor``.
    """
    return sorted(entries, key=functor, reverse=desc)

def sort_by(attributes :list, entries :list, desc: bool = False) -> list:
    """
    Sorts a list of minifold entries.

    Args:
        attributes (list): The list of entry keys used to sort.
        entries (list): A list of minifold entries.
        desc (bool): Pass ``True`` to sort by ascending order,
            ``False`` otherwise.

    Returns:
        The sorted entries, with respect to ``functor``.
    """
    functor = ValuesFromDictFonctor(attributes)
    return sort_by_impl(functor, entries, desc)

class SortByConnector(Connector):
    """
    The :py:class:`SortByConnector` class implements the SORT BY
    statement in a minifold pipeline.
    """
    def __init__(self, attributes: list, child: Connector, desc: bool = False):
        """
        Constructor.

        Args:
            attributes (list): The list of entry keys used to sort.
            child (Connector): The child minifold :py:class:`Connector`
                instance.
        desc (bool): Pass ``True`` to sort by ascending order,
            ``False`` otherwise.
        """
        super().__init__()
        self.m_functor = ValuesFromDictFonctor(attributes)
        self.m_child = child
        self.m_desc = desc

    def attributes(self, object :str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`SortByConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return self.child.attributes(object)

    @property
    def child(self):
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    @property
    def desc(self) -> bool:
        """
        Checks whether this :py:class:`SortByConnector` sorts the entries
        by descending order.

        Returns:
            ``True`` if this :py:class:`SortByConnector` sorts the entries
            by descending order, ``False`` otherwise.
        """
        return self.m_desc

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
            sort_by_impl(
                self.m_functor,
                self.m_child.query(q),
                self.m_desc
            )
        )

    def __str__(self) -> str:
        """
        Returns the string representation of this
        :py:class:`SortByConnector` instance

        Returns:
            The string representation of this
            :py:class:`SortByConnector` instance
        """
        return "SORT BY %s %s" % (
            ", ".join(self.m_functor.attributes),
            "DESC" if self.desc else "ASC"
        )
