#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import re
from minifold.search import (
    contains, contains_words, equals,
    lower_case_equals, lower_case_contains
)

def check_tests(match, tests):
    for (params, expected) in tests:
        print("Calling %s%s, expects %s" % (match.__name__, params, expected))
        obtained = match(*params)
        assert obtained == expected, \
            "Test failed: %s%r != %r (got %r)" % (match.__name__, params, expected, obtained)

def test_contains_words():
    tests = [
        # Basic tests
        (("aa", "xx aa yy", True), True),
        (("aa", "xx AA yy", True), True),
        # Case sensitive
        (("aa", "xx aa yy", False), True),
        (("aa", "xx AA yy", False), False),
        (("aa", "xxaayy",   False), False),
    ]
    check_tests(contains_words, tests)

def test_contains():
    tests = [
        (("aa", "xx aa yy"), True),
        (("aa", "xx AA yy"), False),
        (("aa", "xx aa yy"), True),
        (("aa", "xx AA yy"), False),
        (("aa", "xxaayy"), True),
    ]
    check_tests(contains, tests)

def test_lower_case_contains():
    tests = [
        (("aa", "xx aa yy"), True),
        (("aa", "xx AA yy"), True),
        (("aa", "xx aa yy"), True),
        (("aa", "xx AA yy"), True),
        (("aa", "xxaayy"),   True),
        (("aa", "xxbayy"),   False),
    ]
    check_tests(lower_case_contains, tests)

def test_equals():
    tests = [
        (("aa", "aa"), True),
        (("aa", "x aa y"), False),
        (("aa", "AA"), False),
        (("aa", "bb"), False),
    ]
    check_tests(equals, tests)

def test_lower_case_equals():
    tests = [
        (("aa", "aa"), True),
        (("aa", "x aa y"), False),
        (("aa", "AA"), True),
        (("aa", "bb"), False),
    ]
    check_tests(lower_case_equals, tests)
