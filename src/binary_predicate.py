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

def __includes__(x, y) -> bool:
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
    "IN"  : __includes__,
    "CONTAINS" : operator.__contains__,
}

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
        return "%s %s %s" % (self.left, self.operator, self.right)

    def match(self, entry :dict) -> bool:
#        if self.operator == "&&" or self.operator == "AND":
#            return self.left.match(entry) and self.right.match(entry)
#        elif self.operator == "||" or self.operator == "OR":
#            return self.left.match(entry) or self.right.match(entry)
#        else:
#            try:
#                if self.operator == "==":
#                    return entry[self.left] == self.right
#                elif self.operator == "<=":
#                    return entry[self.left] <= self.right
#                elif self.operator == "<":
#                    return entry[self.left] < self.right
#                elif self.operator == ">=":
#                    return entry[self.left] >= self.right
#                elif self.operator == ">":
#                    return entry[self.left] > self.right
#                elif self.operator == "!=":
#                    return entry[self.left] != self.right
##                elif self.operator == "IN":
##                    return entry[self.left] in self.right
##                elif self.operator == "NOT IN":
##                    return entry[self.left] not in self.right
#                else: raise RuntimeError("Operator not supported %s" % self)
#            except KeyError:
#                if self.operator == "==" and self.right == None: return True
#                return False
        try:
            if self.operator in [operator.__or__, operator.__and__]:
                return self.operator(self.left(entry), self.right(entry))
            else:
                left = entry[self.left]
                right = self.right
                return self.operator(left, right)
        except KeyError:
            return (self.operator == operator.__eq__ and self.right == None)

    def __call__(self, entry :dict) -> bool:
        return self.match(entry)
