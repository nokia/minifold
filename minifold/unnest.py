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

from .query                 import Query, ACTION_READ

def unnest(map_key_unnestedkey :dict, entries :list) -> list:
    ret = list()
    for entry in entries:
        for k, values in entry.items():
            new_attribute = map_key_unnestedkey[k]
            if isinstance(values, list):
                for value in values:
                    ret.append({new_attribute : value})
            else:
                ret.append({new_attribute : values})
    return ret

class UnnestConnector:
    def __init__(self, map_key_unnestedkey :dict, child):
        self.m_child = child
        self.m_map_key_unnestedkey = map_key_unnestedkey

    @property
    def child(self):
        return self.m_child

    def unnest_key(self, key) -> str:
        return self.m_map_key_unnestedkey[key]

    def query(self, q :Query) -> list:
        return self.answer(self.child.query(q))

    def answer(self, entries :list) -> list:
        return unnest(self.m_map_key_unnestedkey)


