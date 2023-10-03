#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

def reverse_dict(d: dict) -> dict:
    """
    Reverses a dictionary (swap its key and its values).
    Note that (key, value) pair may disappear if the values
    are not unique.

    Args:
        d (dict): The input dictionary.

    Returns:
        The reversed dictionary.
    """
    return {
        v: k
        for (k, v) in d.items()
    }


def freeze_dict(d: dict) -> dict:
    """
    Freezes the values of a dictionary (for each value of type ``set``).

    Args:
        d (dict): The input dictionary.

    Returns:
        The freezed dictionary.
    """
    return {
        k: frozenset(v) if isinstance(v, set) else v
        for (k, v) in d.items()
    }
