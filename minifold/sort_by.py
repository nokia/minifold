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
from .values_from_dict      import ValuesFromDictFonctor

def sort_by_impl(fonctor : ValuesFromDictFonctor, entries :list, desc = True) -> list:
    return sorted(entries, key = fonctor, reverse = desc)

def sort_by(attributes :list, entries :list, desc = False) -> list:
    fonctor = ValuesFromDictFonctor(attributes)
    return sort_by_impl(fonctor, entries, desc)

class SortByConnector(Connector):
    def __init__(self, attributes :list, child, desc = False):
        super().__init__()
        self.m_fonctor = ValuesFromDictFonctor(attributes)
        self.m_child = child
        self.m_desc = desc

    def attributes(self, object :str) -> set:
        return self.child.attributes(object)

    @property
    def child(self):
        return self.m_child

    @property
    def desc(self) -> bool:
        return self.m_desc

    def query(self, q :Query) -> list:
        super().query(q)
        return self.answer(
            q,
            sort_by_impl(
                self.m_fonctor,
                self.m_child.query(q),
                self.m_desc
            )
        )

    def __str__(self) -> str:
        return "SORT BY %s %s" % (
            ", ".join(self.m_fonctor.attributes),
            "DESC" if self.desc else "ASC"
        )

