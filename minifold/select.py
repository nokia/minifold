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

def select(entries :list, attributes :list) -> list:
    return [{k : entry[k] for k in attributes} for entry in entries]

class SelectConnector(Connector):
    def __init__(self, child, attributes):
        super().__init__()
        self.m_child = child
        self.m_attributes = attributes

    def attributes(self, object :str) -> set:
        return set(self.m_attributes) & self.m_child.attributes(object)

    @property
    def child(self):
        return self.m_child

    def query(self, query :Query) -> list:
        super().query(query)
        q = query.copy()
        q.attributes = [attribute for attribute in q.attributes if attribute in self.m_attributes]
        return self.answer(
            query,
            select(
                self.m_child.query(q),
                self.m_attributes
            )
        )
