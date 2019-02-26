#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

def cast_none(s :str):
    """
    Cast a string into None if possible.
    Args:
        s: The input str.
    Raises:
        ValueError: if the cast cannot be achieved.
    Returns:
        None if successful.
    """
    if s is None:
        return None
    elif isinstance(s, str) and s.lower() == "none":
        return None
    raise ValueError("Invalid literal for cast_none(): %s" % s)

def cast_bool(s :str) -> bool:
    """
    Cast a string into a bool if possible.
    Args:
        s: The input str.
    Raises:
        ValueError: if the cast cannot be achieved.
    Returns:
        The boolean corresponding to s if successful.
    """
    if isinstance(s, bool):
        return s
    elif isinstance(s, str):
        l = s.lower()
        if l == "true":
            return True
        elif l == "false":
            return False
    raise ValueError("Invalid literal for cast_bool(): %s" % s)

def lexical_cast(s :str, cast):
    """
    Cast a string according to an operator.
    Args:
        cast: The cast operator.
        s: The string to be casted.
    Raises:
        ValueError: if the cast cannot be achieved.
    Returns:
        The corresponding value.
    """
    return cast(s)

def lexical_casts(s :str, cast_operators = [cast_none, cast_bool, int, float]):
    """
    Cast a string according to several cast operators.
    Args:
        s: The string to be casted.
        cast_operators: A list of cast operators. Operators must be ordered
            from the less strict to the more strict (e.g. int before float).
    Returns:
        The original string if no cast worked, the corresponding casted value
        otherwise.
    """
    for cast in cast_operators:
        try:
            ret = lexical_cast(s, cast)
            return ret
        except ValueError:
            pass
    return s
