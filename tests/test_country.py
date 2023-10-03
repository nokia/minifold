#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.country import country_code_to_name


def test_country_code_to_name():
    assert country_code_to_name("FR") == "France"
    assert country_code_to_name("DE") == "Germany"
    assert country_code_to_name("XXX") is None
