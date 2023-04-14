#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

class ValuesFromDictFonctor:
    """
    The :py:class:`ValuesFromDictFonctor` class is an
    internal minifold fonctor used to extract a subset of values
    from a dictionary.

    It is used by several minifold :py:class:`Connector` classes,
    including:

    - :py:class:`GroupByConnector`
    - :py:class:`SortByConnector`
    - :py:class:`UniqueConnector`
    """
    def __init__(self, attributes: list):
        """
        Constructor.

        Args:
            attributes (list): The keys of the values to be extracted.
        """
        self.m_attributes = attributes

    @property
    def attributes(self) -> list:
        """
        Retrieves the keys of interest related to this
        :py:class:`ValuesFromDictFonctor` instance.

        Args:
            The attributes of interest related to this
            :py:class:`ValuesFromDictFonctor` instance.
        """
        return self.m_attributes

    def __call__(self, entry: dict) -> tuple:
        """
        Applies this py:class:`ValuesFromDictFonctor` instance
        to an input dictionary.

        Args:
            entry (dict): An input dictionary.

        Returns:
            The extracted values of interest.
        """
        return tuple(entry.get(k) for k in self.attributes)
