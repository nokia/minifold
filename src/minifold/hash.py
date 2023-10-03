#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

"""
Internals to make hashable object that are not hashable.

This is useful, e.g, in the :py:class:`UniqueConnector` class.
"""


def to_hashable(x: object) -> object:
    """
    Converts an object to an hashable ``tuple``.

    Args:
        x (object): The input object.

    Returns:
        The corresponding hashable object.
    """
    return (
        tuple(
            to_hashable(elt)
            for elt in x
        ) if isinstance(x, (set, list))
        else tuple(
            (to_hashable(k), to_hashable(v))
            for k, v in x.items()
        ) if isinstance(x, dict)
        else x
    )
