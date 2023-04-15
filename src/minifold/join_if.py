#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from .connector import Connector
from .query import Query

"""
This file gathers the functions and the classes related the joins supported
in minifold (excepted the natural join) corresponding in SQL to
the INNER JOIN, LEFT JOIN, RIGHT JOIN
and FULL OUTER JOIN statements.

`This schema <http://4.bp.blogspot.com/-_HsHikmChBI/VmQGJjLKgyI/AAAAAAAAEPw/JaLnV0bsbEo/s1600/sql%2Bjoins%2Bguide%2Band%2Bsyntax.jpg>` recalls their meaning.

See also:
- the :py:class:`NaturalJoinConnector` class;
- the :py:func:`natural_join` function.
"""

INNER_JOIN = 1  # Returns matching records
LEFT_JOIN = 2  # Returns left entries + matching right entries (=> right attributes may be None)
RIGHT_JOIN = 3  # Returns right entries + matching left entries (=> left attributes may be None)
FULL_OUTER_JOIN = 4  # Returns left and right entries while merging matching entries

def merge_dict(l :dict, r :dict) -> dict:
    """
    Merges two dictionaries. The input dictionaries are not altered.

    Example:
        >>> merge_dict({"a": 1, "b": 2}, {"b": 3, "c": 4})
        {'a': 1, 'b': 3, 'c': 4}

    Args:
        l (dict): A dictionary.
        r (dict): Another dictionary.

    Returns:
        The dictionary obtained by merging ``l`` and ``r``.
    """
    ret = l.copy()
    ret.update(r)
    return ret

def join_mode_to_string(mode: int) -> str:
    """
    Convert a ``*_JOIN`` constant to the corresponding string representation.

    Args:
    """
    if mode == INNER_JOIN:
        return "INNER JOIN"
    elif mode == LEFT_JOIN:
        return "LEFT JOIN"
    elif mode == RIGHT_JOIN:
        return "RIGHT JOIN"
    elif mode == FULL_OUTER_JOIN:
        return "FULL OUTER JOIN"
    return "?"

def are_joined_if(l: dict, r: dict, f: callable) -> bool:
    """
    Internal function, used to check whether two dictionaries can be joined
    according to a functor.

    Args:
        l (dict): The dictionary corresponding to the left operand.
        r (dict): The dictionary corresponding to the right operand.
        f (callable): A functor such that ``f(l, r)`` returns
            ``True`` if and only if ``l`` and ``r`` can be joined,
            ``False`` otherwise.

    Raises:
        :py:class:`RuntimeError`, if ``f`` applies
            on keys that are missing in ``l`` or ``r``.

    Returns:
        ``True`` if and only if ``l`` and ``r`` can be joined,
        ``False`` otherwise.
    """
    try:
        return f(l, r)
    except KeyError as e:
        raise RuntimeError("Cannot join\n\tl = %r\n\tr = %r\n%s" % (l, r, e))

def inner_join_if(
    l_entries: list,
    r_entries: list,
    f: callable,
    match_once: bool = True,
    merge: callable = merge_dict
) -> list:
    """
    Computes the INNER JOIN of two lists of minifold entries.

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
            if are_joined_if(l, r, f):
                ret.append(merge(l, r))
                if match_once:
                    break
    return ret

def left_join_if(
    l_entries :list,
    r_entries :list, f,
    match_once = True,
    merge = merge_dict
) -> list:
    """
    Computes the LEFT JOIN of two lists of minifold entries.

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
    if len(r_entries) > 0:
        for l in l_entries:
            joined = False
            r = None
            for r in r_entries:
                if are_joined_if(l, r, f):
                    joined = True
                    ret.append(merge(l, r))
                    if match_once:
                        break
            if joined is False:
                entry = l
                missing_keys = set(r.keys()) - set(l.keys())
                for k in missing_keys:
                    entry[k] = None
                ret.append(entry)
    else:
        ret = l_entries
    return ret

def right_join_if(l_entries :list, r_entries :list, f, match_once = True) -> list:
    """
    Computes the RIGHT JOIN of two lists of minifold entries.

    Args:
        l_entries (dict): The minifold entries corresponding to the left operand.
        r_entries (dict): The minifold entries corresponding to the right operand.
        f (callable): A functor such that ``f(l, r)`` returns
            ``True`` if and only if ``l`` and ``r`` can be joined
            (where ``l`` and ``r`` are two minifold entries),
            ``False`` otherwise.
        match_once (bool): Pass ``True`` if a left entry must be matched
            at most once.

    Returns:
        The corresponding list of entries.
    """
    return left_join_if(r_entries, l_entries, lambda l,r: f(r,l), match_once)

def full_outer_join_if(l_entries :list, r_entries :list, f, match_once = True) -> list:
    """
    Computes the FULL OUTER JOIN of two lists of minifold entries.

    Args:
        l_entries (dict): The minifold entries corresponding to the left operand.
        r_entries (dict): The minifold entries corresponding to the right operand.
        f (callable): A functor such that ``f(l, r)`` returns
            ``True`` if and only if ``l`` and ``r`` can be joined
            (where ``l`` and ``r`` are two minifold entries),
            ``False`` otherwise.
        match_once (bool): Pass ``True`` if a left entry must be matched
            at most once.

    Returns:
        The corresponding list of entries.
    """
    # Get every left entries (join-able or not)
    ret = left_join_if(l_entries, r_entries, f, match_once)

    # Retrieve left keys
    l_keys = set()
    for l in l_entries:
        l_keys |= {k for k in l.keys()}

    # Get missing right entries
    for r in r_entries:
        joined = False
        for l in l_entries:
            if are_joined_if(l, r, f):
                joined = True
                break

        if not joined:
            entry = r
            missing_keys = set(l_keys) - set(r.keys())
            for k in missing_keys:
                entry[k] = None
            ret.append(entry)

    return ret

class JoinIfConnector(Connector):
    """
    The :py:class:`JoinIfConnector` is a minifold connector that implements
    the INNER JOIN, LEFT JOIN, RIGHT JOIN
    and FULL OUTER JOIN statements in a minifold pipeline.
    """
    def __init__(
        self,
        left: Connector,
        right: Connector,
        join_if: callable,
        mode: int = INNER_JOIN
    ):
        """
        Constructor.

        Args:
            left (Connector): The left :py:class:`Connector` child.
            right (Connector): The right :py:class:`Connector` child.
            join_if (callable): The callback implementing the join criterion.
            mode (int): The type of join. The valid values are:
                :py:data:`INNER_JOIN`,
                :py:data:`LEFT_JOIN`,
                :py:data:`RIGHT_JOIN`,
                :py:data:`FULL_OUTER_JOIN`.
        """
        super().__init__()
        self.m_left = left
        self.m_right = right
        self.m_join_if = join_if
        self.m_left_entries = list()
        self.m_right_entries = list()
        self.m_mode = mode

    def attributes(self, object :str):
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

        Raises:
            :py:class:`ValueError` if :py:attr:`self.m_mode` is not valid.

        Returns:
            The list of entries matching the input query.
        """
        super().query(query)
        self.m_left_entries.clear()
        self.m_right_entries.clear()
        self.m_left_entries = self.left.query(query)
        self.m_right_entries = self.right.query(query)
        if self.m_mode == INNER_JOIN:
            entries = inner_join_if(
                self.m_left_entries,
                self.m_right_entries,
                self.m_join_if
            )
        elif self.m_mode == LEFT_JOIN:
            entries = left_join_if(
                self.m_left_entries,
                self.m_right_entries,
                self.m_join_if
            )
        elif self.m_mode == RIGHT_JOIN:
            entries = right_join_if(
                self.m_left_entries,
                self.m_right_entries,
                self.m_join_if
            )
        elif self.m_mode == FULL_OUTER_JOIN:
            entries = full_outer_join_if(
                self.m_left_entries,
                self.m_right_entries,
                self.m_join_if
            )
        else:
            raise ValueError("Invalid mode %s:" % self.m_mode)
        return self.answer(query, entries)

    @property
    def mode(self) -> int:
        """
        Retrieves the join mode used
        in this :py:class:`JoinIfConnector` instance.

        Returns:
            A value among:

            - :py:data:`INNER_JOIN`
            - :py:data:`LEFT_JOIN`
            - :py:data:`RIGHT_JOIN`
            - :py:data:`FULL_OUTER_JOIN`
        """
        return self.m_mode

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

    @property
    def join_if(self) -> callable:
        """
        Retrieves the functor to join entries
        in this :py:class:`JoinIfConnector` instance.

        Returns:
            The left :py:class:`Connector` child.
        """
        return self.m_join_if
