#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import operator
from minifold.binary_predicate import BinaryPredicate, __in__

ENTRY = {"a": 1, "b": 2}
ENTRY2 = {"a": {1, 2, 3}}

def test_le():
    assert BinaryPredicate("a", "<=", 0)(ENTRY) is False
    assert BinaryPredicate("a", "<=", 1)(ENTRY) is True
    assert BinaryPredicate("a", "<=", 3)(ENTRY) is True
    assert BinaryPredicate("a", operator.__le__, 0)(ENTRY) is False
    assert BinaryPredicate("a", operator.__le__, 1)(ENTRY) is True
    assert BinaryPredicate("a", operator.__le__, 3)(ENTRY) is True

def test_lt():
    assert BinaryPredicate("a", "<", 0)(ENTRY) is False
    assert BinaryPredicate("a", "<", 1)(ENTRY) is False
    assert BinaryPredicate("a", "<", 3)(ENTRY) is True
    assert BinaryPredicate("a", operator.__lt__, 0)(ENTRY) is False
    assert BinaryPredicate("a", operator.__lt__, 1)(ENTRY) is False
    assert BinaryPredicate("a", operator.__lt__, 3)(ENTRY) is True

def test_ge():
    assert BinaryPredicate("a", ">=", 0)(ENTRY) is True
    assert BinaryPredicate("a", ">=", 1)(ENTRY) is True
    assert BinaryPredicate("a", ">=", 3)(ENTRY) is False
    assert BinaryPredicate("a", operator.__ge__, 0)(ENTRY) is True
    assert BinaryPredicate("a", operator.__ge__, 1)(ENTRY) is True
    assert BinaryPredicate("a", operator.__ge__, 3)(ENTRY) is False

def test_gt():
    assert BinaryPredicate("a", ">", 0)(ENTRY) is True
    assert BinaryPredicate("a", ">", 1)(ENTRY) is False
    assert BinaryPredicate("a", ">", 3)(ENTRY) is False
    assert BinaryPredicate("a", operator.__gt__, 0)(ENTRY) is True
    assert BinaryPredicate("a", operator.__gt__, 1)(ENTRY) is False
    assert BinaryPredicate("a", operator.__gt__, 3)(ENTRY) is False


def test_eq():
    assert BinaryPredicate("a", "==", 0)(ENTRY) is False
    assert BinaryPredicate("a", "==", 1)(ENTRY) is True
    assert BinaryPredicate("a", "==", 3)(ENTRY) is False
    assert BinaryPredicate("a", operator.__eq__, 0)(ENTRY) is False
    assert BinaryPredicate("a", operator.__eq__, 1)(ENTRY) is True
    assert BinaryPredicate("a", operator.__eq__, 3)(ENTRY) is False

def test_ne():
    assert BinaryPredicate("a", "!=", 0)(ENTRY) is True
    assert BinaryPredicate("a", "!=", 1)(ENTRY) is False
    assert BinaryPredicate("a", "!=", 3)(ENTRY) is True
    assert BinaryPredicate("a", operator.__ne__, 0)(ENTRY) is True
    assert BinaryPredicate("a", operator.__ne__, 1)(ENTRY) is False
    assert BinaryPredicate("a", operator.__ne__, 3)(ENTRY) is True

def test_set():
    assert BinaryPredicate("a", "<=", {1, 2, 3})(ENTRY2) is True
    assert BinaryPredicate("a", "<=", {1, 2, 3, 4})(ENTRY2) is True
    assert BinaryPredicate("a", "<=", {2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", "<=", {2, 3})(ENTRY2) is False

    assert BinaryPredicate("a", "<", {1, 2, 3})(ENTRY2) is False
    assert BinaryPredicate("a", "<", {1, 2, 3, 4})(ENTRY2) is True
    assert BinaryPredicate("a", "<", {2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", "<", {2, 3})(ENTRY2) is False

    assert BinaryPredicate("a", ">=", {1, 2, 3})(ENTRY2) is True
    assert BinaryPredicate("a", ">=", {1, 2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", ">=", {2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", ">=", {2, 3})(ENTRY2) is True

    assert BinaryPredicate("a", ">", {1, 2, 3})(ENTRY2) is False
    assert BinaryPredicate("a", ">", {1, 2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", ">", {2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", ">", {2, 3})(ENTRY2) is True

    assert BinaryPredicate("a", "==", {1, 2, 3})(ENTRY2) is True
    assert BinaryPredicate("a", "==", {1, 2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", "==", {2, 3, 4})(ENTRY2) is False
    assert BinaryPredicate("a", "==", {2, 3})(ENTRY2) is False

    assert BinaryPredicate("a", "!=", {1, 2, 3})(ENTRY2) is False
    assert BinaryPredicate("a", "!=", {1, 2, 3, 4})(ENTRY2) is True
    assert BinaryPredicate("a", "!=", {2, 3, 4})(ENTRY2) is True
    assert BinaryPredicate("a", "!=", {2, 3})(ENTRY2) is True

def test_includes():
    assert BinaryPredicate("a", "IN", {1, 2, 3})(ENTRY) is True
    assert BinaryPredicate("a", "IN", {4, 5, 6})(ENTRY) is False

def test_contains():
    assert BinaryPredicate("a", "CONTAINS", 1)(ENTRY2) is True
    assert BinaryPredicate("a", "CONTAINS", 4)(ENTRY2) is False

def check_clause(t1, f1, t2, f2):
    assert BinaryPredicate(t1, "AND", t2)(ENTRY) is True
    assert BinaryPredicate(t1, "AND", f2)(ENTRY) is False
    assert BinaryPredicate(f1, "AND", t2)(ENTRY) is False
    assert BinaryPredicate(f1, "AND", f2)(ENTRY) is False

    assert BinaryPredicate(t1, "&&", t2)(ENTRY) is True
    assert BinaryPredicate(t1, "&&", f2)(ENTRY) is False
    assert BinaryPredicate(f1, "&&", t2)(ENTRY) is False
    assert BinaryPredicate(f1, "&&", f2)(ENTRY) is False

    assert BinaryPredicate(t1, "OR", t2)(ENTRY) is True
    assert BinaryPredicate(t1, "OR", f2)(ENTRY) is True
    assert BinaryPredicate(f1, "OR", t2)(ENTRY) is True
    assert BinaryPredicate(f1, "OR", f2)(ENTRY) is False

    assert BinaryPredicate(t1, "||", t2)(ENTRY) is True
    assert BinaryPredicate(t1, "||", f2)(ENTRY) is True
    assert BinaryPredicate(f1, "||", t2)(ENTRY) is True
    assert BinaryPredicate(f1, "||", f2)(ENTRY) is False

def test_clause():
    t1 = BinaryPredicate("a", "==", 1)
    f1 = BinaryPredicate("a", "!=", 1)
    t2 = BinaryPredicate("b", "==", 2)
    f2 = BinaryPredicate("b", "!=", 2)
    check_clause(t1, f1, t2, f2)

def test_lambda():
    def t1(e):
        return e["a"] == 1
    def f1(e):
        return e["a"] != 1
    def t2(e):
        return e["b"] == 2
    def f2(e):
        return e["b"] != 2
    check_clause(t1, f1, t2, f2)

def test_in():
    assert not __in__(0, {1, 2, 3})
    assert __in__(1, {1, 2, 3})
    assert __in__(2, {1, 2, 3})
    assert __in__(3, {1, 2, 3})
    assert not __in__(4, {1, 2, 3})
