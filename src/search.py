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

import re
from .where     import where

def equals(x, y) -> bool:
    return x == y
def contains(x, y) -> bool:
    return x in y
def lower_case_equals(x :str, y :str) -> bool:
    return x.lower() == y.lower()
def lower_case_contains(x :str, y :str) -> bool:
    return x.lower() in y.lower()

def contains_words(word, sentence, ignore_case = True):
    pattern = ".*\\b(%s)\\b.*" % word
    flags = re.IGNORECASE if ignore_case else 0
    regex = re.compile(pattern, flags)
    return bool(regex.match(sentence))

class SearchFilter:
    def __init__(self, search_values :list, attributes :list, match):
        self.search_values = search_values
        self.attributes = attributes
        self.match = match

    def __call__(self, entry :dict) -> bool:
        for search_value in self.search_values:
            for attribute in self.attributes:
                if self.match(search_value, entry[attribute]):
                    return True
        return False

def search(
    entries       :list,
    attributes    :list,
    search_values :list,
    match = equals
) -> list:
    return where(entries, SearchFilter(search_values, attributes, match))
