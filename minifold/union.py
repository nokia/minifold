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

from itertools          import chain
from minifold.connector import Connector
from minifold.query     import Query, ACTION_READ

def union_gen(list_entries :list):
    """
    Iterator over a list of list of dicts.
    Args:
        list_entries: A list of lists of dicts.
    Returns:
        The resulting generator.
    """
    return chain(*list_entries)

def union(list_entries :list):
    """
    Make the union of several lists of entries.
    Use minifold.distinct() to remove duplicates.
    Args:
        list_entries: A list of lists of dicts.
    Returns:
        The resulting list of dicts.
    """
    return [entry for entry in union_gen(list_entries)]

class UnionConnector(Connector):
    def __init__(self, childs :list):
        self.m_childs = childs

    def attributes(self, object :str) -> set:
        attrs = set()
        for child in self.m_childs:
            try:
                attrs |= child.attributes(object)
            except:
                pass
        return attrs

    def query(self, query :Query) -> list:
        super().query(query)
        if query.action != ACTION_READ:
            raise ValueError("Invalid action in query %s" % query)
        return union([child.query(query) for child in self.m_childs])

