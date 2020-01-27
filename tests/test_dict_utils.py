#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from minifold.dict_util import reverse_dict

def test_reverse_dict():
    d = {1 : "a", 2 : "b", 3 : "c"}
    assert reverse_dict(d) == {"a" : 1, "b" : 2, "c" : 3}
    d = {1 : "a", 2 : "b", 3 : "c", 4 : "a"}
    assert reverse_dict(d) == {"a" : 1, "b" : 2, "c" : 3} or \
           reverse_dict(d) == {"a" : 4, "b" : 2, "c" : 3}
