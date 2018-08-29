#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
