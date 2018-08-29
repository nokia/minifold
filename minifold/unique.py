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
from .values_from_dict      import ValuesFromDictFonctor

def unique_impl(fonctor :ValuesFromDictFonctor, entries :list) -> list:
    ret = []
    seen_keys = set()
    for entry in entries:
        key = fonctor.get_values(entry)
        if len(key) == 1:
            (key,) = key
        if key not in seen_keys:
            ret.append(entry)
        seen_keys.add(key)
    return ret

def unique(attributes :list, entries :list) -> list:
    fonctor = ValuesFromDictFonctor(attributes)
    return unique_impl(fonctor, entries)

class UniqueConnector:
    def __init__(self, attributes :list, child):
        self.m_fonctor = ValuesFromDictFonctor(attributes)
        self.m_child = child

    @property
    def child(self):
        return self.m_child

    def query(self, q :Query) -> list:
        return self.answer(self.m_child.query(q))

    def answer(self, entries :list) -> list:
        return unique_impl(self.m_fonctor, entries)

    def __str__(self) -> str:
        return "DUP %s" % ", ".join(self.m_fonctor.attributes)

