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

def select(entries :list, attributes :list) -> list:
    return [{k : entry[k] for k in attributes} for entry in entries]

class SelectConnector:
    def __init__(self, child, attributes):
        self.m_child = child
        self.m_attributes = attributes

    @property
    def child(self):
        return self.m_child

    @property
    def attributes(self):
        return self.m_attributes

    def query(self, q :Query) -> list:
        return self.answer(self.m_child.query(q))

    def answer(self, entries :list) -> list:
        return select(entries, self.m_attributes)


