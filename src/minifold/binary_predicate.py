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

import operator
from .dict_util import reverse_dict

def __in__(x, y) -> bool:
    return operator.__contains__(y, x)

OPERATORS = {
    ">"   : operator.__gt__,
    "<"   : operator.__lt__,
    ">="  : operator.__ge__,
    "<="  : operator.__le__,
    "=="  : operator.__eq__,
    "!="  : operator.__ne__,
    "||"  : operator.__or__,
    "OR"  : operator.__or__,
    "&&"  : operator.__and__,
    "AND" : operator.__and__,
    "^"   : operator.__xor__,
    "XOR" : operator.__xor__,
    "IN"  : __in__,
    "CONTAINS" : operator.__contains__,
}

OPERATORS_TO_STR = reverse_dict(OPERATORS)

class BinaryPredicate:
    def __init__(self, left, operator, right):
        self.m_left     = left
        self.m_operator = OPERATORS.get(operator, operator)
        self.m_right    = right
        assert not isinstance(self.m_operator, str)

    @property
    def left(self):
        return self.m_left

    @property
    def operator(self):
        return self.m_operator

    @property
    def right(self):
        return self.m_right

    def __str__(self) -> str:
        return "%s %s %s" % (self.left, OPERATORS_TO_STR[self.operator], self.right)

    def match(self, entry :dict) -> bool:
        try:
            if self.operator in [operator.__or__, operator.__and__, operator.__xor__]:
                return self.operator(self.left(entry), self.right(entry))
            else:
                left = entry[self.left]
                right = self.right
                return self.operator(left, right)
        except KeyError:
            return (self.operator == operator.__eq__ and self.right == None)

    def __call__(self, entry :dict) -> bool:
        return self.match(entry)
