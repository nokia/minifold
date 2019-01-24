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

from enum import IntEnum

class DocType(IntEnum):
    BOOKS_AND_THESES = 0 # Books and Theses
    ARTICLE          = 1 # ART, Conference and Workshop Papers
    COMMUNICATION    = 2 # COMM
    JOURNAL          = 3 # Journal Articles
    REPORT           = 4 # Report, Informal Publications
    POSTER           = 5 # POSTER
    HDR              = 6 # HDR
    CHAPTER          = 7 # COUV, Editorship
    PATENT           = 8 # PATENT
    UNKNOWN          = 9999 # UNDEFINED or ""

    def __str__(self) -> str:
        s = IntEnum.__str__(self)
        class_name = "%s" % self.__class__.__name__
        s = s[len(class_name)+1:]
        s = s.replace("_", " ")
        return s.title()

    def __lt__(self, other) -> bool:
        return self.value < other.value

def doc_type_to_html(t :DocType, n :int = 1) -> str:
    # Default %s is not wonderful
    if   t == DocType.UNKNOWN: ret = "Misc"
    elif t == DocType.CHAPTER: ret = "Editorship"
    elif t == DocType.JOURNAL: ret = "Journal article"
    else: ret = "%s" % t

    # Add "s" at the end if needed
    if n > 1 and t not in [DocType.BOOKS_AND_THESES, DocType.HDR, DocType.CHAPTER, DocType.UNKNOWN]:
        ret = "%ss" % ret

    return ret


