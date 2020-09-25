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

from minifold.log import Log

try:
    import pycountry
except ImportError as e:
    Log.warning("Please install pycountry: apt-get install python3-pycountry")
    raise e

def _country_code_to_name(country_code :str) -> str:
    # For obsolete version of pycountry
    Log.warning("Please update python3-pycountry; apt-get update && apt-get upgrade")

    ret = None

    try:
        country = pycountry.countries.get(alpha_2 = country_code.upper())
        ret = country.name
    except KeyError as e:
        Log.warning("Unknown country %r" % country_code)

    return ret

def country_code_to_name(country_code :str) -> str:
    if country_code == None:
        return None

    ret = None
    try:
        country = pycountry.countries.get(alpha_2 = country_code.upper())
        if country is None:
            return None
        ret = country.name
    except KeyError as e:
        if "%s" % e == "alpha_2":
            ret = _country_code_to_name(country_code)
        else:
            Log.warning("Unknown country %r" % country_code)

    return ret
