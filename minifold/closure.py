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


def is_multiple_key(key) -> bool:
    return isinstance(key, (set, frozenset, list))

def closure(key, fds) -> set:
    ret = (key | {k for k in key}) if is_multiple_key(key) else {key}
    changed = True

    i = 0
    while changed == True:
        changed = False
        i += 1
        for (key, column) in fds:
            if key in ret and column not in ret:
                ret.add(column)
                changed = True

    if is_multiple_key(key):
        ret.remove(key)

    return ret


def minimal_cover(fds :set) -> list:
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

    def edge_to_pair(e :EdgeDescriptor, g :DirectedGraph) -> tuple:
        return (source(e, g), target(e, g))

    def minimal_cover_graph(g :DirectedGraph) -> set:
        return minimal_cover({edge_to_pair(e, g) for e in edges(g)})
except ImportError:
    pass

