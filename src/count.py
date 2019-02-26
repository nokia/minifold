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

from .connector             import Connector
from .query                 import Query, ACTION_READ

def count_gen(gen) -> int:
    """
    Count the number of elements listed by a generator.
    Args:
        gen: A generator.
    Returns:
        The number of elements listed by a generator.
    """
    n = 0
    for x in gen: n += 1
    return n

def count(entries :list) -> int:
    """
    Count the number of entries.
    Args:
        entries: A list of entries
    Returns:
        The number of element in entries
    """
    return len(entries)

class CountConnector(Connector):
    def __init__(self, child :Connector):
        super().__init__()
        self.m_child = child

    def query(self, query :Query) -> int:
        super().query(query)
        if query.action != ACTION_READ:
            raise ValueError("Invalid action in query %s" % query)
        return count(self.m_child.query(query))
