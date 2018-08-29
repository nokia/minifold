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

def sort_by_impl(fonctor : ValuesFromDictFonctor, entries :list, reverse = True) -> list:
    return sorted(entries, key = fonctor.get_values, reverse = reverse)

def sort_by(attributes :list, entries :list, reverse = False) -> list:
    fonctor = ValuesFromDictFonctor(attributes)
    return sort_by_impl(fonctor, entries, reverse)

class SortByConnector:
    def __init__(self, attributes :list, child, reverse = False):
        self.m_fonctor = ValuesFromDictFonctor(attributes)
        self.m_child = child
        self.m_reverse = reverse

    @property
    def child(self):
        return self.m_child

    @property
    def reverse(self) -> bool:
        return self.m_reverse

    def query(self, q :Query) -> list:
        return self.answer(self.m_child.query(q))

    def answer(self, entries :list) -> list:
        return sort_by_impl(self.m_fonctor, entries, self.m_reverse)

    def __str__(self) -> str:
        return "SORT BY %s" % ", ".join(self.m_fonctor.attributes)


