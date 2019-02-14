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

def lambdas(map_lambdas :dict, entries :list, attributes :set = None) -> list:
    attrs = set(map_lambdas.keys())
    if attributes:
        attrs &= set(attributes)
    for entry in entries:
        for attr, func in map_lambdas.items():
            if attr in attrs:
                try:
                    entry[attr] = func(entry)
                except KeyError:
                    entry[attr] = None
    return entries

class LambdasConnector(Connector):
    def __init__(self, map_lambdas :dict, child):
        super().__init__()
        self.m_child = child
        self.m_map_lambdas = map_lambdas

    @property
    def child(self):
        return self.m_child

    def attributes(self, object :str) -> set:
        return self.m_child.attributes(object) | set(self.m_map_lambdas.keys())

    def query(self, q :Query) -> list:
        #matching_lambdas_keys = set(q.attributes) & set(self.m_map_lambdas.keys())
        #if len(matching_lambdas_keys):
        #    Log.warning("LambdasConnector::query: attributes in %s won't be fetched" % matching_lambdas_keys)

        # TODO :
        # - if q.attributes involves a field in m_map_lambdas.keys(), select(q.attributes, self.child(SELECT * ...))
        # - if q.filters    involves a field in m_map_lambdas.keys(), where(q.filters, self.child(... WHERE True))
        super().query(q)
        return self.answer(
            q,
            lambdas(
                self.m_map_lambdas,
                self.child.query(q),
                q.attributes
            )
        )
