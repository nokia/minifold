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
    """
    The :py:class:`DocType` class enumerates the different kind of
    scientific publication.

    See also:

    - :py:class:`HalConnector`
    - :py:class:`DblpConnector`
    """
    BOOKS_AND_THESES = 0     # Books and Theses
    ARTICLE          = 1     # ART, Conference and Workshop Papers
    COMMUNICATION    = 2     # COMM
    JOURNAL          = 3     # Journal Articles
    REPORT           = 4     # Report, Informal Publications
    POSTER           = 5     # POSTER
    HDR              = 6     # HDR
    CHAPTER          = 7     # COUV, Editorship
    PATENT           = 8     # PATENT
    UNKNOWN          = 9999  # UNDEFINED or ""

    def __str__(self) -> str:
        """
        Converts a :py:class:`DocType` instance to the corresponding string.

        Returns:
            The corresponding string representation.
        """
        s = IntEnum.__str__(self)
        class_name = "%s" % self.__class__.__name__
        s = s[len(class_name)+1:]
        s = s.replace("_", " ")
        return s.title()

    def __lt__(self, other) -> bool:
        """
        Compares this :py:class:`DocType` instance to another one.

        Args:
            other (DocType): Another :py:class:`DocType` instance.

        Returns:
            ``True`` if ``self`` is lower than ``other``.
        """
        return self.value < other.value

def doc_type_to_html(t: DocType, n: int = 1) -> str:
    """
    Builds the HTML label related to a collection of homogeneous documents.

    Args:
        t (DocType): The type of the documents.
        n (int): The number of document.

    Returns:
        The corresponding HTML label.
    """
    ret = (
        "Misc"            if t == DocType.UNKNOWN else
        "Editorship"      if t == DocType.CHAPTER else
        "Journal article" if t == DocType.JOURNAL else
        t
    )

    # Add "s" at the end if needed
    if n > 1 and t not in {
        DocType.BOOKS_AND_THESES,
        DocType.HDR,
        DocType.CHAPTER,
        DocType.UNKNOWN
    }:
        ret = f"{ret}s"

    return ret
