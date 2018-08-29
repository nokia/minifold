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

class ValuesFromDictFonctor:
    def __init__(self, attributes :list):
        self.m_attributes = attributes

    @property
    def attributes(self) -> list:
        return self.m_attributes

    def get_values(self, entry :dict) -> tuple:
        ret = tuple()
        for key in self.attributes:
            try:
                ret += (entry[key],)
            except KeyError as e:
                raise KeyError("Entry %r has no key named %r" % (entry, key))
        return ret

