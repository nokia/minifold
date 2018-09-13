#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Usage:
#     python3 setup.py install
#     python3 setup.py bdist_rpm

import os
from setuptools import find_packages, setup

__version__        = (0, 9, 1)
ROOT_PATH          = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION   = open(os.path.join(ROOT_PATH, "README.rst")).read()

# Copy is only triggered if the file does not yet exists.

setup(
    name             = "minifold",
    version          = ".".join(["%s" % x for x in __version__]),
    description      = "minifold",
    long_description = LONG_DESCRIPTION,
    author           = "Marc-Olivier Buob",
    author_email     = "marc-olivier.buob@nokia-bell-labs.com",
    url              = "http://github.com/nokia/minifold",
    license          = "BSD-3",
    zip_safe         = False,
    packages         = find_packages(),
    requires         = ["typing"],
    package_dir      = {"minifold" : "minifold"},
)
