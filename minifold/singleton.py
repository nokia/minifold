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

# Based on https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

class Singleton(type):
    s_instances = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.s_instances:
            cls.s_instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.s_instances[cls]
