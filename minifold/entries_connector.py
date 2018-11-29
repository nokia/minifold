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

    def query(self, q :Query) -> list:
        super().query(q)
        ret = list()
        if q.action == ACTION_READ:
            queried_attributes = set(q.attributes) & self.keys if len(q.attributes) > 0 else self.keys
            if len(queried_attributes) > 0:
                fetched = 0
                for raw_entry in self.entries[q.offset:]:
                    if q.filters == None or q.filters.match(raw_entry):
                        ret.append({k : raw_entry.get(k) for k in queried_attributes})
                        fetched += 1
                        if fetched == q.limit: break
        else:
            raise RuntimeError("EntriesConnector::query: %s not yet implemented" % action_to_str(q.action))
        return self.answer(ret)

    @property
    def keys(self) -> set:
        return self.m_keys

    @property
    def entries(self) -> list:
        return self.m_entries


