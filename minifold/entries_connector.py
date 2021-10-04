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

from .connector  import Connector
from .query      import Query, ACTION_READ, action_to_str

class EntriesConnector(Connector):
    def __init__(self, entries :list):
        super().__init__()
        self.m_keys = set()
        if len(entries) > 0:
            for entry in entries:
                self.m_keys |= set(entry.keys())
        self.m_entries = entries

    def attributes(self, obj :str = None) -> set:
        return set(self.m_keys)

    def query(self, query :Query) -> list:
        super().query(query)
        ret = list()
        if query.action == ACTION_READ:
            ret = self.reshape_entries(query, self.entries)
        else:
            raise RuntimeError("EntriesConnector::query: %s not yet implemented" % action_to_str(query.action))
        return self.answer(query, ret)

    @property
    def entries(self) -> list:
        return self.m_entries


