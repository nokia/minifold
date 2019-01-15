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
from .hash                  import to_hashable
from .query                 import Query, ACTION_READ
from .values_from_dict      import ValuesFromDictFonctor

def group_by_impl(fonctor :ValuesFromDictFonctor, entries :list) -> dict:
    ret = dict()
    for entry in entries:
        key = fonctor(entry)
        if len(key) == 1:
            (key,) = key
        key = to_hashable(key)
        if key not in ret.keys(): ret[key] = list()
        ret[key].append(entry)
    return ret

def group_by(attributes :list, entries :list) -> list:
    fonctor = ValuesFromDictFonctor(attributes)
    return group_by_impl(fonctor, entries)

class GroupByConnector(Connector):
    def __init__(self, attributes :list, child):
        super().__init__()
        self.m_fonctor = ValuesFromDictFonctor(attributes)
        self.m_child = child

    @property
    def child(self):
        return self.m_child

    def attributes(self, object :str):
        return set(self.m_fonctor.attributes)

    def query(self, q :Query) -> list:
        super().query(q)
        return self.answer(
            q,
            group_by_impl(
                self.m_fonctor,
                self.m_child.query(q)
            )
        )

    def __str__(self) -> str:
        return "GROUP BY %s" % ", ".join(self.m_fonctor.attributes)

