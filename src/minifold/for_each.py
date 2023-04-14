#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

class ForEachFilter:
    """
    The :py:class:`ForEachFilter` class is useful when an
    minifold entry (i.e., a dictionary) maps a key with a
    value which is a list of sub-entries.

    It filters each sub-entries that do not match the set
    of provided filters.
    """
    def __init__(self, attribute_name: str, map_filter: dict):
        """
        Constructor.

        Args:
            attribute_name (str): The key of the minifold entry
                attribute mapped with a list of sub-entries.
            map_filter (dict): A ``dict(sub_key : filter)``
                where `̀`sub_key`` corresponds to an (optional) sub-entry key
                and ``filter`` is a ``callable(object) -> bool`` returning
                ``True`` if and only if the value mapped to `̀`sub_key``
                indicates that the sub-entry must be filtered,
                ``False`` otherwise.
        """
        self.attribute_name = attribute_name
        self.map_filter = map_filter

    def match_filters(self, sub_entry: dict) -> bool:
        """
        Checks whether a sub-entry is filtered according to this
        :py:class:`ForEachFilter` instance.

        Args:
            sub_entry (dict): The sub-entry to be checked.

        Returns:
            ``True`` if ``sub_entry`` is not filtered,
            ``False`` otherwise.
        """
        for attribute, keep in self.map_filter.items():
            if attribute in sub_entry.keys():
                if not keep(sub_entry[attribute]):
                    return False
        return True

    def __call__(self, entry: dict) -> bool:
        """
        Fonctor method, filtering each sub-entry filtered
        by this :py:class:`ForEachFilter`.

        Args:
            entry (dict): The minifold entry.

        Returns:
            ``True`` if successful.
        """
        sub_entries = entry.get(self.attribute_name)

        if not sub_entries:
            return True

        entry[self.attribute_name] = [
            sub_entry
            for sub_entry in sub_entries
            if self.match_filters(sub_entry)
        ]

        return True

def for_each_sub_entry(entry, attribute: str, map_lambda: dict) -> dict:
    """
    Applies a set of lambda functions to the sub-entries carried by
    a minifold entry (key, value) pair.

    Args:
        attribute (str): The key of ``entry`` carrying the sub-entries
            to be processed.
        map_lambda (dict): A ``dict(sub_key : transform)`` where:
            ``sub_key`` is an (optional) key involved in a sub-entry;
            ``transform`` is a function transforming the value mapped
            to ``sub_key`` to its new value.

    Returns:
        The modified entry.
    """
    entry[attribute] = [
        {
            k: map_lambda[k](v) if k in map_lambda.keys() else v
            for (k, v) in sub_entry.items()
        }
        for sub_entry in entry[attribute]
    ]
    return entry
