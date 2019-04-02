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
from .query                 import Query

def where(entries :list, f) -> list:
    return [entry for entry in entries if f(entry)]

class WhereConnector(Connector):
    def __init__(self, child, keep_if):
        super().__init__()
        self.m_child = child
        self.m_keep_if = keep_if

    @property
    def child(self):
        return self.m_child

    def attributes(self, object :str) -> set:
        return self.child.attributes(object)

    @property
    def keep_if(self):
        return self.m_keep_if

    def query(self, q :Query) -> list:
        super().query(q)
        return self.answer(
            q,
            where(
                self.m_child.query(q),
                self.m_keep_if
            )
        )

