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

    def __call__(self, entry :dict) -> tuple:
        return tuple(entry.get(k) for k in self.attributes)

