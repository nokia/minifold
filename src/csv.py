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

import io, csv
from enum       import Enum

from .connector import Connector
from .query     import Query, ACTION_READ, action_to_str

class CsvModeEnum(Enum):
    FILENAME = 0 # Use text file
    STRING   = 1 # Use str
    TEXTIO   = 2 # Use any class inheriting TextIOBase

    def __str__(self) -> str:
        s = Enum.__str__(self)
        i = len(self.__class__.__name__)
        return s[i + 1:]

from minifold.log import Log
Log.enable_print = True
class CsvConnector(Connector):
    def __init__(
        self,
        data      :str,        # filename | csv_str | TextIOBase
        delimiter :chr         = ' ',
        quotechar :chr         = '"',
        mode      :CsvModeEnum = CsvModeEnum.FILENAME
    ):
        super().__init__()
        Log.debug(mode)
        stream = open(data, "rt")  if mode == CsvModeEnum.FILENAME else \
                 io.StringIO(data) if mode == CsvModeEnum.STRING   else \
                 data              if mode == CsvModeEnum.TEXTIO   else \
                 None
        if not stream:
            raise RuntimeError("CsvConnector: Invalid input stream (data = %r, mode = %s)" % (data, mode))

        # csv.reader cannot directly process a str, so we use a io.StringIO
        # See https://stackoverflow.com/questions/3305926/python-csv-string-to-array
        Log.debug("delimiter = %r, quotechar = %r" % (delimiter, quotechar))
        Log.debug(type(stream))
        reader = csv.reader(stream, delimiter=delimiter, quotechar=quotechar)
        rows = [row for row in reader]
        Log.debug(rows)

        if mode == CsvModeEnum.FILENAME and stream:
            stream.close()

        # Assuming that keys are declared in the first line of the CSV data.
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
                        entry = {k : v for k, v in raw_entry.items() if k in queried_attributes}
                        missing_attributes = set(queried_attributes) - set(entry.keys())
                        for k in missing_attributes:
                            entry[k] = None
                        ret.append(entry)
        else:
            raise RuntimeError("CsvConnector.query: %s not yet implemented" % action_to_str(q.action))
        return self.answer(q, ret)

    @property
    def keys(self) -> set:
        return self.m_keys

    @property
    def entries(self) -> list:
        return self.m_entries


