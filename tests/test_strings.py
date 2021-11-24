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

from minifold.strings import remove_punctuation, to_international_string, to_canonic_fullname

def test_to_international_string_lower():
    s_in  = "ÁÀÄĆÇĐÉÊÈËÍÎÏŁÖÔÛÜŠáàäćçđéêèëíîïłöôûüšß"
    s_out = "AAACCDEEEEIIILOOUUSaaaccdeeeeiiiloouusss"
    assert to_international_string(s_in) == s_out

def test_remove_ponctuation():
    s_in  = "a,,ä;â.à:a a"
    s_out = "a  ä â à a a"
    assert remove_punctuation(s_in) == s_out

def test_to_canonic_fullname():
    assert to_canonic_fullname("firstname1-firstname2 lastname")   == "firstname1 firstname2 lastname"
    assert to_canonic_fullname("firstname (surname) lastname")     == "firstname lastname"
    assert to_canonic_fullname("<b>firstname</b> <i>lastname</i>") == "firstname lastname"
    assert to_canonic_fullname("firstname X. lastname")            == "firstname lastname"
    assert to_canonic_fullname("  firstname   lastname ")          == "firstname lastname"
    assert to_canonic_fullname("\\it firstname lastname ")         == "firstname lastname"
