#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query, ACTION_READ, action_to_str

class EntriesConnector(Connector):
    """
    :py:class:`EntriesConnector` wraps a list of minifold entries
    (list of dictionaries)
    """
    def __init__(self, entries: list):
        """
        Constructor.

        Args:
            entries (list): A list of minifold entries.
        """
        super().__init__()
        self.m_keys = set()
        if len(entries) > 0:
            for entry in entries:
                self.m_keys |= set(entry.keys())
        self.m_entries = entries

    def attributes(self, obj: str = None) -> set:
        """
        Lists available attributes related to a given collection of object
        stored in this :py:class:`EntriesConnector` instance.

        Args:
            obj (str): The name of the collection of entries.
                As :py:class:`EntriesConnector` manages a single connection
                you may pass ``None``.

        Returns:
            The set of available attributes.
        """
        return set(self.m_keys)

    def query(self, query: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input Query.
        """
        super().query(query)
        if query.action == ACTION_READ:
            ret = self.reshape_entries(query, self.entries)
        else:
            action = action_to_str(query.action)
            raise RuntimeError(
                f"EntriesConnector.query: {action} not yet implemented"
            )
        return self.answer(query, ret)

    @property
    def entries(self) -> list:
        """
        Accessor to the entries nested in this :py:class:`EntriesConnector` instance.

        Returns:
            The nested entries.
        """
        return self.m_entries
