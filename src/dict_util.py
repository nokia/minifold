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

def reverse_dict(d :dict) -> dict:
    return {v : k for (k, v) in d.items()}

def freeze_dict(d :dict):
    return {k : frozenset(v) if isinstance(v, set) else v for (k, v) in d.items()}
