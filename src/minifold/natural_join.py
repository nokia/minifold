#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# If you need more generic join, see join_if.py
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query     import Query
from .join_if   import merge_dict

def are_naturally_joined(l: dict, r: dict) -> bool:
    """
    Internal function, used to check whether two dictionaries can be joined
    using an NATURAL JOIN statement.

    Args:
        l (dict): The dictionary corresponding to the left operand.
        r (dict): The dictionary corresponding to the right operand.

    Returns:
        ``True`` if and only if ``l`` and ``r`` can be joined,
        ``False`` otherwise (i.e., ``l`` and ``r`` have no common key).
    """
    inter_keys = set(l.keys()) & set(r.keys())
    if len(inter_keys) == 0:
        return False
    for key in inter_keys:
        if l[key] != r[key]:
            return False
    return True

def natural_join(l_entries: list, r_entries: list) -> list:
    """
    Computes the NATURAL JOIN of two lists of minifold entries.

    Args:
        l_entries (dict): The minifold entries corresponding to the left operand.
        r_entries (dict): The minifold entries corresponding to the right operand.
        f (callable): A functor such that ``f(l, r)`` returns
            ``True`` if and only if ``l`` and ``r`` can be joined
            (where ``l`` and ``r`` are two minifold entries),
            ``False`` otherwise.
        match_once (bool): Pass ``True`` if a left entry must be matched
            at most once.
        merge (callable): A function that merges two input dictionaries.
            Defaults to :py:func:`merge_dict`.

    Returns:
        The corresponding list of entries.
    """
    ret = list()
    for l in l_entries:
        for r in r_entries:
            if are_naturally_joined(l, r):
                ret.append(merge_dict(l, r))
    return ret

class NaturalJoinConnector(Connector):
    """
    The :py:class:`NaturalJoinConnector` is a minifold connector that implements
    the NATURAL JOIN statement in a minifold pipeline.
    """
    def __init__(self, left: Connector, right: Connector):
        """
        Constructor.

        Args:
            left (Connector): The left :py:class:`Connector` child.
            right (Connector): The right :py:class:`Connector` child.
        """
        super().__init__()
        self.m_left = left
        self.m_right = right
        self.m_left_entries = list()
        self.m_right_entries = list()

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`JoinIfConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return (
            self.m_left.attributes(object) |
            self.m_right.attributes(object)
        )

    def query(self, query: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """

        self.m_left_entries.clear()
        self.m_right_entries.clear()
        self.m_left_entries = self.left.query(query)
        self.m_right_entries = self.right.query(query)
        return self.answer(
            query,
            natural_join(self.m_left_entries, self.m_right_entries)
        )

    @property
    def left(self) -> Connector:
        """
        Retrieves the left :py:class:`Connector` child
        in this :py:class:`JoinIfConnector` instance.

        Returns:
            The left :py:class:`Connector` child.
        """
        return self.m_left

    @property
    def right(self) -> Connector:
        """
        Retrieves the right :py:class:`Connector` child
        in this :py:class:`JoinIfConnector` instance.

        Returns:
            The left :py:class:`Connector` child.
        """
        return self.m_right
