#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pprint             import pprint

from minifold.doc_type  import DocType
from minifold.dblp      import DblpConnector
from minifold.hal       import HalConnector

if __name__ == '__main__':
    x = DocType.HDR
    y = DocType.BOOKS_AND_THESES
    print("x = %s" % x)
    print("y = %s" % x)
    print("x < y = %s" % (x < y))
    print("sorted = %s" % sorted([y, x]))

    print("\nTest DBLP\n")
    for s in ["conference and workshop papers", "conference or workshop", "journal articles", "informal publications", "books and theses", "editorship"]:
        x = DblpConnector.to_doc_type(s)
        print("%s --> %s" % (s, x))

    print("\nTest HAL\n")
    for s in ["art", "comm", "report", "hdr", "couv", "patent"]:
        x = HalConnector.to_doc_type(s)
        print("%s --> %s" % (s, x))

    sys.exit(0)
