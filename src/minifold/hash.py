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

def to_hashable(x):
    return tuple(to_hashable(elt) for elt in x) if isinstance(x, (set, list)) \
      else tuple((to_hashable(k), to_hashable(v)) for k, v in x.items()) if isinstance(x, dict) \
      else x
