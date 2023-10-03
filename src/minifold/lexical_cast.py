#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

def cast_none(s: str) -> None:
    """
    Casts a string to ``None`` if possible, raises an exception otherwise.

    Args:
        s (str): The string to be casted.

    Raises:
        ValueError: if the cast cannot be achieved.

    Returns:
        ``None`` if successful.
    """
    if s is None:
        return None
    elif isinstance(s, str) and s.lower() == "none":
        return None
    raise ValueError("Invalid literal for cast_none(): %s" % s)


def cast_bool(s: str) -> bool:
    """
    Casts a string to a ``bool`` if possible, raises an exception otherwise.

    Args:
        s (str): The string to be casted.

    Raises:
        ``ValueError``, if the cast cannot be achieved.

    Returns:
        The boolean corresponding to s if successful.
    """
    if isinstance(s, bool):
        return s
    elif isinstance(s, str):
        sl = s.lower()
        if sl == "true":
            return True
        elif sl == "false":
            return False
    raise ValueError("Invalid literal for cast_bool(): %s" % s)


def lexical_cast(s: str, cast: callable) -> object:
    """
    Casts a string according to an operator.
    See also the :py:func:`lexical_casts` function.

    Args:
        s (str): The string to be casted.
        cast (callable): A single cast operator.
            _Examples:_ :py:func:`cast_bool`, :py:func:`cast_none`,
            :py:func:`int`, :py:func:`float`, etc.

    Raises:
        ``ValueError``, if the cast cannot be achieved.

    Returns:
        The corresponding value.
    """
    return cast(s)


def lexical_casts(s: str, cast_operators: list = None) -> object:
    """
    Casts a string according to several cast operators.
    See also the :py:func:`lexical_cast` function.

    Args:
        s (str): The string to be casted.
        cast_operators: A list of cast operators. Operators must be ordered
            by decreasing strictness (e.g. ``int`` should preceed ``float``).
            Pass ``None`` to use the default list of cast operators.

    Returns:
        The original string if no cast worked, the corresponding casted value
        otherwise.
    """
    if cast_operators is None:
        cast_operators = [cast_none, cast_bool, int, float]
    for cast in cast_operators:
        try:
            ret = lexical_cast(s, cast)
            return ret
        except ValueError:
            pass
    return s
