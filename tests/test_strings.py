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

from minifold.strings import to_canonic_fullname

if __name__ == '__main__':

    fullnames = [
        "Diana Zeaiter-Joumblatt",
        "Marc-Olivier Buob",
        "Salah Eddine-Elayoubi"
    ]

    for fullname in fullnames:
        print("%r --> %r" % (fullname, to_canonic_fullname(fullname)))

    sys.exit(0)
