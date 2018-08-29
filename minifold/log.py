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

import sys

class Log:
    # TODO: leave enable_print to False before committing
    # TODO: implement log level
    # TODO: load log level from config file
    enable_print = False

    @classmethod
    def info(self, s):
        if Log.enable_print == True: print("INFO: %s" % s, file = sys.stderr)

    @classmethod
    def error(self, s):
        if Log.enable_print == True: print("ERROR: %s" % s, file = sys.stderr)

    @classmethod
    def warning(self, s):
        if Log.enable_print == True: print("WARNING: %s" % s, file = sys.stderr)
