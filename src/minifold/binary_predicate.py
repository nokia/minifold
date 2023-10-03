#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import operator
from .dict_util import reverse_dict


def __in__(x: object, y: iter) -> bool:
    """
    Checks whether ``x`` is in ``y``.

    Args:
        x (object): An item.
        y (iter): A container.

    Returns:
        ``True`` iff ``x in y``,
        ``False`` otherwise.
    """
    return operator.__contains__(y, x)


OPERATORS = {
    ">": operator.__gt__,
    "<": operator.__lt__,
    ">=": operator.__ge__,
    "<=": operator.__le__,
    "==": operator.__eq__,
    "!=": operator.__ne__,
    "||": operator.__or__,
    "OR": operator.__or__,
    "&&": operator.__and__,
    "AND": operator.__and__,
    "^": operator.__xor__,
    "XOR": operator.__xor__,
    "IN": __in__,
    "CONTAINS": operator.__contains__,
}

OPERATORS_TO_STR = reverse_dict(OPERATORS)


class BinaryPredicate:
    """
    The :py:class:`BinaryPredicate` represents a binary predicate
    to define minifold queries.
    See also the :py:class:`Query` class (especially, the ``filters`` attribute).
    """
    def __init__(self, left, operator, right):
        """
        Constructor.

        Example:
            >>> from minifold import BinaryPredicate
            >>> bp = BinaryPredicate("a", "<=", 0)
            >>> entry = {"a": 1, "b": 2}
            >>> bp(entry)
            False
            >>> entry = {"a": -1, "b": 2}
            >>> bp(entry)
            True

        Args:
            left (str): The left operand. Maybe the key of an entry.
            operator (str): The binary operator, see also :py:data:`OPERATORS`.
            right (str): The right operand. Cannot be the key of an entry.
        """
        self.m_left = left
        self.m_operator = OPERATORS.get(operator, operator)
        self.m_right = right
        assert not isinstance(self.m_operator, str)

    @property
    def left(self) -> str:
        """
        Retrieves the left operand of this :py:class:`BinaryPredicate`.

        Returns:
            The left operand of this :py:class:`BinaryPredicate`.
        """
        return self.m_left

    @property
    def operator(self) -> str:
        """
        Retrieves the binary operator of this :py:class:`BinaryPredicate`.

        Returns:
            The binary operator of this :py:class:`BinaryPredicate`.
        """
        return self.m_operator

    @property
    def right(self):
        """
        Retrieves the right operand of this :py:class:`BinaryPredicate`.

        Returns:
            The right operand of this :py:class:`BinaryPredicate`.
        """
        return self.m_right

    def __str__(self) -> str:
        """
        Converts this :py:class:`BinaryPredicate` to a string.

        Returns:
            The string representing this :py:class:`BinaryPredicate`.
        """
        return "%s %s %s" % (self.left, OPERATORS_TO_STR[self.operator], self.right)

    def match(self, entry: dict) -> bool:
        """
        Matches an entry against this :py:class:`BinaryPredicate`.

        Args:
            entry (dict): An entry. One of its key must corresponds to ``self.left``.

        Raises:
            KeyError: if the entry does not have key matching ``self.left``.

        Returns:
            ``True`` if this :py:class:`BinaryPredicate` is satisfied by ``entry``,
            ``False`` otherwise.
        """
        try:
            if self.operator in [operator.__or__, operator.__and__, operator.__xor__]:
                return self.operator(self.left(entry), self.right(entry))
            else:
                left = entry[self.left]
                right = self.right
                return self.operator(left, right)
        except KeyError:
            return (self.operator == operator.__eq__ and self.right is None)

    def __call__(self, entry: dict) -> bool:
        """
        Short-hand for the :py:meth:`BinaryPredicate.match` method.

        Args:
            entry (dict): An entry. One of its key must corresponds to ``self.left``.

        Raises:
            KeyError: if the entry does not have key matching ``self.left``.

        Returns:
            ``True`` if this :py:class:`BinaryPredicate` is satisfied by ``entry``,
            ``False`` otherwise.
        """
        return self.match(entry)
