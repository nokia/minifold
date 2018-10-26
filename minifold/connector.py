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

from .query     import Query
from .log       import Log

class Connector:
    enable_debug = False

    def __init__(self):
        pass

    def query(self, q :Query) -> list:
        if Connector.enable_debug:
            Log.debug("%s: --> %s" % (self.__class__.__name__, q))
        # This method must be overloaded

    def answer(self, entries :list) -> list:
        if Connector.enable_debug:
            Log.debug("%s: <-- %s" % (self.__class__.__name__, "\n".join([str(entry) for entry in entries])))
        return entries
