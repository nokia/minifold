#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.lexical_cast import cast_none, cast_bool, lexical_cast, lexical_casts


def test_cast_none():
    for none in ["none", "None", "NONE", None]:
        assert cast_none(none) is None, "cast_none(%r) should return None"
    for dummy in [True, False, 0, 0.0, "dummy", 1, 1.2]:
        try:
            _ = cast_none(dummy)
            assert False, "cast_none(%r) should raise ValueError" % dummy
        except ValueError:
            pass


def test_cast_bool():
    for true in ["true", "True", "TRUE"]:
        assert cast_bool(true) is True, "cast_bool(%r) should return True"
    for false in ["false", "False", "FALSE"]:
        assert cast_bool(false) is False, "cast_bool(%r) should return False"
    for dummy in [None, 0, 0.0, "dummy", 1, 1.2]:
        try:
            _ = cast_bool(dummy)
            assert False, "cast_bool(%r) should raise ValueError" % dummy
        except ValueError:
            pass


def test_lexical_cast():
    assert lexical_cast("None", cast_none) is None
    assert lexical_cast("True", cast_bool) is True
    assert lexical_cast("False", cast_bool) is False
    assert lexical_cast("17", int) == 17
    try:
        lexical_cast("17.2", int) == 17
        assert False, "lexical_cast('17.2', int) should raise ValueError"
    except ValueError:
        pass
    assert lexical_cast("17", float) == 17.0
    assert lexical_cast("17.2", float) == 17.2


def test_lexical_casts():
    cast_operators = [cast_none, cast_bool, int, float]
    assert lexical_casts("None", cast_operators) is None
    assert lexical_casts("True", cast_operators) is True
    assert lexical_casts("False", cast_operators) is False
    assert lexical_casts("17", cast_operators) == 17
    assert lexical_casts("17.2", cast_operators) == 17.2
