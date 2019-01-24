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
from enum       import IntEnum

from .connector import Connector
from .query     import Query, ACTION_READ, action_to_str
from .log       import Log

class CsvModeEnum(IntEnum):
    FILENAME = 0 # Use text file
    STRING   = 1 # Use str
    TEXTIO   = 2 # Use any class inheriting TextIOBase

    def __str__(self) -> str:
        s = IntEnum.__str__(self)
        i = len(self.__class__.__name__)
        return s[i + 1:]

class CsvConnector(Connector):
    def __init__(
        self,
        data      :str,        # filename | csv_str | TextIOBase
        delimiter :chr         = ' ',
        quotechar :chr         = '"',
        mode      :CsvModeEnum = CsvModeEnum.FILENAME
    ):
        super().__init__()
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

        # Assuming that attributes are declared in the first line of the CSV data.
        self.indexed_attributes = rows[0]
        self.entries = [{self.indexed_attributes[i] : v for i, v in enumerate(row)} for row in rows[1:]]

    def attributes(self, object :str):
        return set(self.indexed_attributes)

    def query(self, query :Query) -> list:
        super().query(query)
        ret = list()
        if query.action == ACTION_READ:
            ret = self.reshape_entries(query, self.entries)
        else:
            raise RuntimeError("CsvConnector.query: %s not yet implemented" % action_to_str(query.action))
        return self.answer(query, ret)

