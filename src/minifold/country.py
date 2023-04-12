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

"""
This file provides utilities to wrap the ``pycountry`` python module.
"""

from .log import Log

try:
    import pycountry
except ImportError as e:
    from .log import Log
    Log.warning(
        "\n".join([
            "Please install requests",
            "  APT: sudo apt install python3-pycountry",
            "  PIP: sudo pip3 install --upgrade pycountry",
        ])
    )
    raise e

def _country_code_to_name(country_code :str) -> str:
    """
    Fixes an obsolete country code.

    Args:
        country_code (str): The input country code.

    Returns:
        The fixed country code.
    """
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
    """
    Retrieves the name of a country given its code.

    Args:
        country_code (str): The input country code.

    Returns:
        The corresponding country name.
    """

    if country_code is None:
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
