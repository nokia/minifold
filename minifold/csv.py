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

import csv

from .connector             import Connector
from .query                 import Query, ACTION_READ, action_to_str

class CsvConnector(Connector):
    def __init__(self, filename :str, delimiter=' ', quotechar='"'):
        super().__init__()
        reader = csv.reader(open(filename, "rt"), delimiter=delimiter, quotechar=quotechar)
        rows = [row for row in reader]
        self.m_keys = rows[0]
        self.m_entries = [{self.m_keys[i] : v for i, v in enumerate(row)} for row in rows[1:]]

    def query(self, q :Query) -> list:
        super().query(q)
        ret = list()
        if q.action == ACTION_READ:
            queried_attributes = set(q.attributes) & set(self.keys) if len(q.attributes) > 0 else self.keys
            if len(queried_attributes) > 0:
                for raw_entry in self.entries:
                    if q.filters == None or q.filters.match(raw_entry):
                        entry = {k:v for k,v in raw_entry.items() if k in queried_attributes}
                        missing_attributes = set(queried_attributes) - set(entry.keys())
                        for k in missing_attributes:
                            entry[k] = None
                        ret.append(entry)
        else:
            raise RuntimeError("EntriesConnector::query: %s not yet implemented" % action_to_str(q.action))
        return self.answer(ret)

    @property
    def keys(self) -> set:
        return self.m_keys

    @property
    def entries(self) -> list:
        return self.m_entries


