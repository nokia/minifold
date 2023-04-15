#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import re
from .where import where

def equals(x: object, y: object) -> bool:
    """
    Tests whether two objects are equal (wraps the ``==`` operator).

    Examples:
        >>> equals("foo", "foo")
        True
        >>> equals("foo", "FOO")
        False

    Args:
        x (object): An object.
        y (object): An object.

    Returns:
        ``True`` if and only if ``x == y``,
        ``False`` otherwise.
    """
    return x == y

def contains(x: object, y: object) -> bool:
    """
    Tests whether two objects are equal (wraps the ``==`` operator).

    Example:
        >>> equals("bar", "foobar")
        True

    Args:
        x (object): An object.
        y (object): An object.

    Returns:
        ``True`` if and only if ``x in y``,
        ``False`` otherwise.
    """
    return x in y

def lower_case_equals(x: str, y: str) -> bool:
    """
    Checks whether two string are equals without considering the case.

    Example:
        >>> lower_case_equals("foo", "FOO")
        True

    Args:
        x (str): A string.
        y (str): A string.

    Returns:
        ``True`` if and only if the both strings are equal without considering the case,
        ``False`` otherwise.
    """
    return x.lower() == y.lower()

def lower_case_contains(x: str, y: str) -> bool:
    """
    Checks whether a string is included in another one without considering the case.

    Example:
        >>> lower_case_contains("foo", "barFOObar")
        True

    Args:
        x (str): The search string.
        y (str): The queried string.

    Returns:
        ``True`` if and only if the both strings are equal without considering the case,
        ``False`` otherwise.
    """
    return x.lower() in y.lower()

def contains_words(word: str, sentence: str, ignore_case: bool = True):
    """
    Checks whether a word is contained in a string (e.g., a sentence).

    Examples:
        >>> contains_words("earth", "Earth is a planet.")
        True
        >>> contains_words("earth", "A terrible earthquake.")
        False

    Args:
        word (str): The searched word.
        sentence (str): The queried string.
        ignore_case (bool): Pass `True` if the search is not case sensitive,
            ``False`` otherwise. Defaults to ``True``.

    Returns:
        ``True`` if ``word`` has been found in ``sentence``,
        ``False`` otherwise.
    """
    pattern = ".*\\b(%s)\\b.*" % word
    flags = re.IGNORECASE if ignore_case else 0
    regex = re.compile(pattern, flags)
    return bool(regex.match(sentence))

class SearchFilter:
    """
    The :py:class:`SearchFilter` implements a minifold filter allowing
    to filter minifold entries based on a search predicate.
    """
    def __init__(self, search_values: list, attributes: list, match: callable):
        """
        Constructor.

        Args:
            search_values (list): The searched values.
            attributes (list): The attributes of interest.
            match (callable): The search strategy, e.g.,
                :py:func:`equals`,
                :py:func:`contains`.
                If the values are string, you could also consider:
                :py:func:`lower_case_contains`,
                :py:func:`lower_case_equals`,
                :py:func:`contains_words`.
        """
        self.search_values = search_values
        self.attributes = attributes
        self.match = match

    def __call__(self, entry: dict) -> bool:
        """
        Functor method.

        Args:
            entry (dict): A minifold entry.

        Returns:
            ``True`` if ``entry`` is matched by the search,
            ``False`` otherwise.
        """
        for search_value in self.search_values:
            for attribute in self.attributes:
                if self.match(search_value, entry[attribute]):
                    return True
        return False

def search(
    entries: list,
    attributes: list,
    search_values: list,
    match: callable = equals
) -> list:
    """
    Searches the entries whose at least one attribute of interest is matched
    a searched word

    Args:
        entries (list): A list of minifold entries.
        attributes (list): The attributes of interest.
        search_values (list): The searched values.
        match (callable): The search strategy, e.g.,
            :py:func:`equals`,
            :py:func:`contains`.
            If the values are string, you could also consider:
            :py:func:`lower_case_contains`,
            :py:func:`lower_case_equals`,
            :py:func:`contains_words`.

    Returns:
        The subset of entries matched by the search.
    """
    return where(entries, SearchFilter(search_values, attributes, match))
