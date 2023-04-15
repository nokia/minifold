#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query

def unnest(map_key_unnestedkey: dict, entries: list) -> list:
    """
    Implements the ``unnest`` PostgresSQL function for a list of minifold entries.

    Example:
        >>> unnest({"a": "A", "b": "B"}, [{"a" : [1, 2, 3], "b" : [10, 20, 30]}])
        [{'A': 1}, {'A': 2}, {'A': 3}, {'B': 10}, {'B': 20}, {'B': 30}]

    Args:
        map_key_unnestedkey (dict): A dictionary which maps key corresponding
            to its corresponding unnested key.
        entries (list): A list of minifold entries.

    Returns:
        The list unnested entries. Each entry is a dictionary with a single
        key-value pair, where the key is an unnested key.
    """

    ret = list()
    for entry in entries:
        # NOTE: This only works if entries a single key matching map_key_unnestedkey
        for (k, values) in entry.items():
            new_attribute = map_key_unnestedkey.get(k)
            if isinstance(values, list):
                for value in values:
                    ret.append({new_attribute : value})
            else:
                ret.append({new_attribute : values})
    return ret

class UnnestConnector(Connector):
    """
    The :py:class:`UnnestConnector` class implements the unnest
    function (in PostgreSQL) in a minifold pipeline.
    """
    def __init__(self, map_key_unnestedkey: dict, child: Connector):
        """
        Constructor.

        Args:
            child (Connector): The child minifold :py:class:`Connector` instance.
        """
        super().__init__()
        self.m_child = child
        self.m_map_key_unnestedkey = map_key_unnestedkey

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`UnnestConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        raise NotImplementedError

    @property
    def child(self) -> Connector:
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    def unnest_key(self, key: str) -> str:
        """
        Retrieves the unnested key corresponding to a given key.

        Args:
            key (str): A key identifying an minifold entry
                attribute whose value is a list.

        Raises:
            :py:class:`KeyError` if ``key`` is not in ``self.m_map_key_unnestedkey``.

        Returns:
            The corresponding unnested key.
        """
        return self.m_map_key_unnestedkey[key]

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
            unnest(
                self.m_map_key_unnestedkey,
                self.child.query(q)
            )
        )
