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
    """
    Enumeration listing the different kind of supported CSV data source.
    """
    FILENAME = 0  # Use text file
    STRING   = 1  # Use str
    TEXTIO   = 2  # Use any class inheriting TextIOBase

    def __str__(self) -> str:
        s = IntEnum.__str__(self)
        i = len(self.__class__.__name__)
        return s[i + 1:]

class CsvConnector(Connector):
    def __init__(
        self,
        data: str,
        delimiter: chr = ' ',
        quotechar: chr = '"',
        mode: CsvModeEnum = CsvModeEnum.FILENAME
    ):
        """
        Constructor.

        Args:
            data (str): Depending on the nature of the CSV data source,
                this string either contains the path to the CSV file;
                or the CSV data itself; or the ``TextIOBase`` instance.
                See the ``mode`` parameter.
            delimiter (str): The string that delimits each column of the
                input CSV. Example: ``";"``, ``"|"``, ``" "``.
                Defaults to ``' '``.
            quotechar (str): The charater used to delimits values
                that may contain ``delimiter``. Defaults to ``'"'``.
            mode (CsvModeEnum): The nature of the input CSV source.
                See also the :py:class:`CsvModeEnum` enumeration.
        """
        super().__init__()
        stream = (
            open(data, "rt")  if mode == CsvModeEnum.FILENAME else
            io.StringIO(data) if mode == CsvModeEnum.STRING   else
            data              if mode == CsvModeEnum.TEXTIO   else
            None
        )
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
        self.entries = [
            {self.indexed_attributes[i] : v
            for (i, v) in enumerate(row)} for row in rows[1:]
        ]

    def attributes(self, object: str):
        """
        Lists the attributes of the collection of objects stored
        in this :py:class:`CsvConnector` instance.

        Args:
            object: The name of the minifold object.
                As a :py:class:`CsvConnector` instance stores a single
                collection, ``object`` is no relevant and you may pass ``None``.

        Returns:
            The set of available ``object``'s attributes
        """
        return set(self.indexed_attributes)

    def query(self, query: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching ``query``.
        """
        super().query(query)
        if query.action == ACTION_READ:
            ret = self.reshape_entries(query, self.entries)
        else:
            raise RuntimeError(
                "CsvConnector.query: %s not yet implemented" % action_to_str(query.action)
            )
        return self.answer(query, ret)
