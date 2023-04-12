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


def is_multiple_key(key: object) -> bool:
    """
    Checks whether a key is a multiple key (i.e., a key involving
    multiple attributes).

    Args:
        key (object): A key. Possible types are ``str`` or ``set``,
            ``frozenset`` or ``list`` of strings.

    Returns:
        ``True`` if and only if ``key`` is multiple,
        ``False`` otherwise.
    """
    return isinstance(key, (set, frozenset, list))

def closure(key: object, fds: dict) -> set:
    """
    Compute the closure of a key given a set of functional dependencies.

    Args:
        key (object): A key. Possible types are ``str`` or ``set``,
            ``frozenset`` or ``list`` of strings.
        fds (dict): A dictionary where each key-value pair represents
            a functional dependency (by mapping a key with another key).

    Returns:
        The "reachable" attributes from ``key``.
    """
    ret = (key | {k for k in key}) if is_multiple_key(key) else {key}
    changed = True

    while changed:
        changed = False
        for (key, column) in fds:
            if key in ret and column not in ret:
                ret.add(column)
                changed = True

    if is_multiple_key(key):
        ret.remove(key)

    return ret

def minimal_cover(fds: set) -> set:
    """
    Retricts a set of functional dependencies to make it 3-NF.

    Args:
        fds (dict): A dictionary where each key-value pair represents
            a functional dependency (by mapping a key with another key).

    Returns:
        The corresponding subset of functional dependencies.
    """
    min_fds = fds.copy()

    for (key, column) in fds:
        # Try to remove (key, column) and see if we cover the closure remains the same
        if column in closure(key, min_fds - {(key, column)}):
            min_fds -= {(key, column)}

    for (key, column) in min_fds.copy():
        if is_multiple_key(key):
            # Check whether each k attribute is required, otherwise, discard it.
            for k in key:
                if k in closure(key - k, min_fds - {(key, column)}):
                    min_fds -= {(key, column)}
                    min_fds |= {(key - k, column)}

    return min_fds

try:
    from pybgl.graph import DirectedGraph, EdgeDescriptor, edges, source, target

    def edge_to_pair(e: EdgeDescriptor, g: DirectedGraph) -> tuple:
        """
        Converts an arc to a pair of vertices.

        Args:
            e (EdgeDescriptor): An arc of the graph.
            g (DirectedGraph): A graph.

        Returns:
            A ``(u, v)`` pair where
            ``u`` is the source of ``e`` in ``g`` and
            ``v`` is the target of ``e`` in ``g``.
        """
        return (source(e, g), target(e, g))

    def minimal_cover_graph(g :DirectedGraph) -> set:
        """
        Computes the minimal cover set of functional dependencies
        given a graph where each vertex corresponding to an attribute
        and each directed arc to a functional dependency.

        Args:
            g (DirectedGraph): A graph.

        Returns:
            The set of 3-NF functional dependencies.
        """
        return minimal_cover({edge_to_pair(e, g) for e in edges(g)})
except ImportError:
    pass
