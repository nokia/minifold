#!/usr/bin/env pytest-3
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
from minifold.binary_predicate import BinaryPredicate

ENTRY = {"a" : 1, "b" : 2}
ENTRY2 = {"a" : {1, 2, 3}}

def test_le():
    assert BinaryPredicate("a", "<=", 0)(ENTRY) == False
    assert BinaryPredicate("a", "<=", 1)(ENTRY) == True
    assert BinaryPredicate("a", "<=", 3)(ENTRY) == True
    assert BinaryPredicate("a", operator.__le__, 0)(ENTRY) == False
    assert BinaryPredicate("a", operator.__le__, 1)(ENTRY) == True
    assert BinaryPredicate("a", operator.__le__, 3)(ENTRY) == True

def test_lt():
    assert BinaryPredicate("a", "<", 0)(ENTRY) == False
    assert BinaryPredicate("a", "<", 1)(ENTRY) == False
    assert BinaryPredicate("a", "<", 3)(ENTRY) == True
    assert BinaryPredicate("a", operator.__lt__, 0)(ENTRY) == False
    assert BinaryPredicate("a", operator.__lt__, 1)(ENTRY) == False
    assert BinaryPredicate("a", operator.__lt__, 3)(ENTRY) == True

def test_ge():
    assert BinaryPredicate("a", ">=", 0)(ENTRY) == True
    assert BinaryPredicate("a", ">=", 1)(ENTRY) == True
    assert BinaryPredicate("a", ">=", 3)(ENTRY) == False
    assert BinaryPredicate("a", operator.__ge__, 0)(ENTRY) == True
    assert BinaryPredicate("a", operator.__ge__, 1)(ENTRY) == True
    assert BinaryPredicate("a", operator.__ge__, 3)(ENTRY) == False

def test_gt():
    assert BinaryPredicate("a", ">", 0)(ENTRY) == True
    assert BinaryPredicate("a", ">", 1)(ENTRY) == False
    assert BinaryPredicate("a", ">", 3)(ENTRY) == False
    assert BinaryPredicate("a", operator.__gt__, 0)(ENTRY) == True
    assert BinaryPredicate("a", operator.__gt__, 1)(ENTRY) == False
    assert BinaryPredicate("a", operator.__gt__, 3)(ENTRY) == False

def test_eq():
    assert BinaryPredicate("a", "==", 0)(ENTRY) == False
    assert BinaryPredicate("a", "==", 1)(ENTRY) == True
    assert BinaryPredicate("a", "==", 3)(ENTRY) == False
    assert BinaryPredicate("a", operator.__eq__, 0)(ENTRY) == False
    assert BinaryPredicate("a", operator.__eq__, 1)(ENTRY) == True
    assert BinaryPredicate("a", operator.__eq__, 3)(ENTRY) == False

def test_ne():
    assert BinaryPredicate("a", "!=", 0)(ENTRY) == True
    assert BinaryPredicate("a", "!=", 1)(ENTRY) == False
    assert BinaryPredicate("a", "!=", 3)(ENTRY) == True
    assert BinaryPredicate("a", operator.__ne__, 0)(ENTRY) == True
    assert BinaryPredicate("a", operator.__ne__, 1)(ENTRY) == False
    assert BinaryPredicate("a", operator.__ne__, 3)(ENTRY) == True

def test_set():
    assert BinaryPredicate("a", "<=", {1, 2, 3})(ENTRY2)    == True
    assert BinaryPredicate("a", "<=", {1, 2, 3, 4})(ENTRY2) == True
    assert BinaryPredicate("a", "<=", {2, 3, 4})(ENTRY2)    == False
    assert BinaryPredicate("a", "<=", {2, 3})(ENTRY2)       == False

    assert BinaryPredicate("a", "<", {1, 2, 3})(ENTRY2)    == False
    assert BinaryPredicate("a", "<", {1, 2, 3, 4})(ENTRY2) == True
    assert BinaryPredicate("a", "<", {2, 3, 4})(ENTRY2)    == False
    assert BinaryPredicate("a", "<", {2, 3})(ENTRY2)       == False

    assert BinaryPredicate("a", ">=", {1, 2, 3})(ENTRY2)    == True
    assert BinaryPredicate("a", ">=", {1, 2, 3, 4})(ENTRY2) == False
    assert BinaryPredicate("a", ">=", {2, 3, 4})(ENTRY2)    == False
    assert BinaryPredicate("a", ">=", {2, 3})(ENTRY2)       == True

    assert BinaryPredicate("a", ">", {1, 2, 3})(ENTRY2)    == False
    assert BinaryPredicate("a", ">", {1, 2, 3, 4})(ENTRY2) == False
    assert BinaryPredicate("a", ">", {2, 3, 4})(ENTRY2)    == False
    assert BinaryPredicate("a", ">", {2, 3})(ENTRY2)       == True

    assert BinaryPredicate("a", "==", {1, 2, 3})(ENTRY2)    == True
    assert BinaryPredicate("a", "==", {1, 2, 3, 4})(ENTRY2) == False
    assert BinaryPredicate("a", "==", {2, 3, 4})(ENTRY2)    == False
    assert BinaryPredicate("a", "==", {2, 3})(ENTRY2)       == False

    assert BinaryPredicate("a", "!=", {1, 2, 3})(ENTRY2)    == False
    assert BinaryPredicate("a", "!=", {1, 2, 3, 4})(ENTRY2) == True
    assert BinaryPredicate("a", "!=", {2, 3, 4})(ENTRY2)    == True
    assert BinaryPredicate("a", "!=", {2, 3})(ENTRY2)       == True

def test_includes():
    assert BinaryPredicate("a", "IN", {1, 2, 3})(ENTRY) == True
    assert BinaryPredicate("a", "IN", {4, 5, 6})(ENTRY) == False

def test_contains():
    assert BinaryPredicate("a", "CONTAINS", 1)(ENTRY2) == True
    assert BinaryPredicate("a", "CONTAINS", 4)(ENTRY2) == False

def check_clause(t1, f1, t2, f2):
    assert BinaryPredicate(t1, "AND", t2)(ENTRY) == True
    assert BinaryPredicate(t1, "AND", f2)(ENTRY) == False
    assert BinaryPredicate(f1, "AND", t2)(ENTRY) == False
    assert BinaryPredicate(f1, "AND", f2)(ENTRY) == False

    assert BinaryPredicate(t1, "&&", t2)(ENTRY) == True
    assert BinaryPredicate(t1, "&&", f2)(ENTRY) == False
    assert BinaryPredicate(f1, "&&", t2)(ENTRY) == False
    assert BinaryPredicate(f1, "&&", f2)(ENTRY) == False

    assert BinaryPredicate(t1, "OR", t2)(ENTRY) == True
    assert BinaryPredicate(t1, "OR", f2)(ENTRY) == True
    assert BinaryPredicate(f1, "OR", t2)(ENTRY) == True
    assert BinaryPredicate(f1, "OR", f2)(ENTRY) == False

    assert BinaryPredicate(t1, "||", t2)(ENTRY) == True
    assert BinaryPredicate(t1, "||", f2)(ENTRY) == True
    assert BinaryPredicate(f1, "||", t2)(ENTRY) == True
    assert BinaryPredicate(f1, "||", f2)(ENTRY) == False

def test_clause():
    t1 = BinaryPredicate("a", "==", 1)
    f1 = BinaryPredicate("a", "!=", 1)
    t2 = BinaryPredicate("b", "==", 2)
    f2 = BinaryPredicate("b", "!=", 2)
    check_clause(t1, f1, t2, f2)

def test_lambda():
    t1 = lambda e: e["a"] == 1
    f1 = lambda e: e["a"] != 1
    t2 = lambda e: e["b"] == 2
    f2 = lambda e: e["b"] != 2
    check_clause(t1, f1, t2, f2)
