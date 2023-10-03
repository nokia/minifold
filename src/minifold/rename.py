#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from copy import deepcopy
from .binary_predicate import BinaryPredicate
from .dict_util import reverse_dict
from .connector import Connector
from .query import Query


def rename_list(values: list, mapping: dict) -> list:
    """
    Replaces some values involved in a list.

    Example:
        >>> rename_list(["a", "b", "a", "c"], {"a": "A", "b": "B"})
        ['A', 'B', 'A', 'c']

    Args:
        values (list): The input list, modified in place.
        mapping (dict): A dictionary mapping each value to
            be replaced by the new corresponding value.

    Returns:
        The updated list.
    """
    for (i, value) in enumerate(values):
        try:
            values[i] = mapping[value]
        except KeyError:
            pass  # see test_dblp.py
    return values


def rename_key(d: dict, old_key: str, new_key: str) -> dict:
    """
    Replaces a key (possibly) involved in a dictionary.

    Example:
        >>> rename_key({"a": 1, "b": 2, "c": 3}, "a", "A")
        {'b': 2, 'c': 3, 'A': 1}

    Args:
        d (dict): The input dictionary, updated in place.
        old_key (str): The key to be updated.
        new_key (str): The new key.

    Returns:
        The updated dictionary.
    """
    try:
        d[new_key] = d.pop(old_key)
    except KeyError:
        pass
    return d


def rename_entry(d: dict, mapping: dict) -> dict:
    """
    Replaces several keys (possibly) involved in a dictionary.

    Example:
        >>> rename_entry({"a": 1, "b": 2, "c": 3}, {"a": "A", "b": "B"})
        {'c': 3, 'A': 1, 'B': 2}

    Args:
        d (dict): The input dictionary, updated in place.
        mapping (dict): A dictionary mapping each key to
            be replaced by the new corresponding key.

    Returns:
        The updated dictionary.
    """
    for (old_key, new_key) in mapping.items():
        rename_key(d, old_key, new_key)
    return d


def rename(mapping: dict, entries: list) -> list:
    """
    Replaces several keys (possibly) involved in a list of minifold entries.

    Example:
        >>> rename({"a": "A", "b": "B"}, [{"a": 1, "b": 2, "c": 3}, {"a": 10, "b": 20, "c": 30}])
        [{'c': 3, 'A': 1, 'B': 2}, {'c': 30, 'A': 10, 'B': 20}]

    Args:
        mapping (dict): A dictionary mapping each key to
            be replaced by the new corresponding key.
        entries (list): A list of minifold entries, updated in place.

    Returns:
        The updated entries.
    """
    for entry in entries:
        rename_entry(entry, mapping)
    return entries


# TODO minifold.searchSearchFilter is not supported
def rename_filters(filters: object, mapping: dict):
    """
    Rename the keys involved in a list of minifold filters
    (see :py:class:`BinaryPredicate`), typically the WHERE
    part of a :py:class:`Query` instance.
    Recursive function.
    See the :py:func:`rename_query` function.

    Args:
        filters (object): The minifold filters, updated in place.
        mapping (dict): A dictionary mapping each key to
            be replaced by the new corresponding key.


    Returns:
        The updated filters.
    """
    if filters is None or isinstance(filters, int) or isinstance(filters, tuple):
        pass
    elif isinstance(filters, str):
        try:
            filters = mapping[filters]
        except KeyError:
            pass
    elif isinstance(filters, BinaryPredicate):
        filters.m_left = rename_filters(filters.left, mapping)
        filters.m_right = rename_filters(filters.right, mapping)
    else:
        raise RuntimeError("rename_filters: unsupported type %s: filters = %s" % (type(filters), filters))
    return filters


def rename_sort_by(sort_by: dict, mapping: dict) -> dict:
    """
    Rename the SORT BY part of a :py:class:`Query` instance.
    See the :py:func:`rename_query` function.

    Args:
        sort_by (dict): The SORT BY part of a :py:class:`Query` instance.
        mapping (dict): A dictionary mapping each key to
            be replaced by the new corresponding key.

    Returns:
        The dictionary corresponding to ``sort_by`` after renaming.
    """
    return {
        mapping.get(attribute, attribute): sort_asc
        for attribute, sort_asc in sort_by.items()
    } if sort_by else dict()


def rename_query(q: Query, mapping: dict) -> Query:
    """
    Rename some attributes involved in a :py:class:`Query` instance.
    This is especially useful when a minifold pipeline involves several
    data sources using different naming conventions for a same attribute.

    Args:
        q (Query); A py:class:`Query` instance.
        mapping (dict): A dictionary mapping each key to
            be replaced by the new corresponding key.

    Returns:
        The renamed minifold query.
    """
    q_renamed = q
    rename_list(q_renamed.attributes, mapping)
    rename_filters(q_renamed.filters, mapping)
    q.sort_by = rename_sort_by(q_renamed.sort_by, mapping)
    return q_renamed


class RenameConnector(Connector):
    """
    The :py:class:`RenameConnector` class wraps the :py:func:`rename` function
    to exploit it in a minifold query plan.
    """
    def __init__(self, mapping: dict = None, child: Connector = None):
        """
        Constructor.

        Args:
            mapping (dict): A dictionary mapping each key to
                be replaced by the new corresponding key
                (overlying to underlying ontology).
                Note that mapping must be reversible, i.e.
                ``reverse_dict(reverse_dict(d)) == d``.
            child (Connector): The child minifold :py:class:`Connector`
                instance.
        """
        super().__init__()
        self.m_map_rq = mapping if mapping else dict()
        self.m_map_qr = reverse_dict(mapping)
        self.m_child = child

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`RenameConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return {
            self.map_rq.get(attribute, attribute)
            for attribute in self.m_child.attributes(object)
        }

    def query(self, q: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """
        super().query(q)
        assert self.child is not None
        q_renamed = rename_query(deepcopy(q), self.map_qr)
        return self.answer(
            q,
            rename(
                self.map_rq,
                self.child.query(q_renamed)
            )
        )

    @property
    def child(self):
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    @property
    def map_qr(self):
        """
        Accessor to the renaming mapping (overlying to underlying).

        Returns:
            The corresponding mapping.
        """
        return self.m_map_qr

    @property
    def map_rq(self):
        """
        Accessor to the renaming mapping (underlying to overlying).

        Returns:
            The corresponding mapping.
        """
        return self.m_map_rq
