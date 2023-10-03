#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import io
import os
import sys

from minifold.csv import CsvConnector, CsvModeEnum
from minifold.query import Query

CSV_STRING = """col1,col2,col3
1,2,3
1111,22222,333
"11,1",222,333
"""

DELIMITER = ","
QUOTECHAR = "\""

EXPECTED = [
    {"col1": "1", "col2": "2", "col3": "3"},
    {"col1": "1111", "col2": "22222", "col3": "333"},
    {"col1": "11,1", "col2": "222", "col3": "333"},
]

CSV_FILENAME = os.path.join(sys.path[0], "data.csv")


def test_csv_string():
    connector = CsvConnector(
        CSV_STRING,
        delimiter=DELIMITER,
        quotechar=QUOTECHAR,
        mode=CsvModeEnum.STRING
    )
    obtained = connector.query(Query())
    assert obtained == EXPECTED


def test_csv_stringio():
    stream = io.StringIO(CSV_STRING)
    connector = CsvConnector(
        stream,
        delimiter=DELIMITER,
        quotechar=QUOTECHAR,
        mode=CsvModeEnum.TEXTIO
    )
    obtained = connector.query(Query())
    assert obtained == EXPECTED


def test_csv_textiowrapper():
    with open(CSV_FILENAME) as stream:
        connector = CsvConnector(
            stream,
            delimiter=DELIMITER,
            quotechar=QUOTECHAR,
            mode=CsvModeEnum.TEXTIO
        )
        obtained = connector.query(Query())
        assert obtained == EXPECTED


def test_csv_filename():
    connector = CsvConnector(
        CSV_FILENAME,
        delimiter=DELIMITER,
        quotechar=QUOTECHAR,
        mode=CsvModeEnum.FILENAME
    )
    obtained = connector.query(Query())
    assert obtained == EXPECTED


def test_csv_attributes():
    stream = io.StringIO(CSV_STRING)
    connector = CsvConnector(
        stream,
        delimiter=DELIMITER,
        quotechar=QUOTECHAR,
        mode=CsvModeEnum.TEXTIO
    )
    assert connector.attributes("") == {"col1", "col2", "col3"}
