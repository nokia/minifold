#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# If you need more generic join, see join_if.py
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from .connector import Connector
from .query     import Query, ACTION_READ
from .join_if   import merge_dict

def are_naturally_joined(l :dict, r :dict) -> bool:
    inter_keys = set(l.keys()) & set(r.keys())
    if len(inter_keys) == 0:
        return False
    for key in inter_keys:
        if l[key] != r[key]:
            return False
    return True

def natural_join(l_entries :list, r_entries :list) -> list:
    ret = list()
    for l in l_entries:
        for r in r_entries:
            if are_naturally_joined(l, r):
                ret.append(merge_dict(l, r))
    return ret

class NaturalJoinConnector(Connector):
    def __init__(self, left, right):
        self.m_left = left
        self.m_right = right
        self.m_left_entries = list()
        self.m_right_entries = list()

    def attributes(self, object :str) -> set:
        return self.m_left.attributes(object) \
             | self.m_right.attributes(object)

    def query(self, query :Query) -> list:
        self.m_left_entries.clear()
        self.m_right_entries.clear()
        self.m_left_entries = self.left.query(query)
        self.m_right_entries = self.right.query(query)
        return self.answer(
            query,
            natural_join(self.m_left_entries, self.m_right_entries)
        )

    @property
    def left(self):
        return self.m_left

    @property
    def right(self):
        return self.m_right


