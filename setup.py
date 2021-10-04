#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Usage:
#     python3 setup.py install
#     python3 setup.py bdist_rpm

from setuptools import find_packages, setup

__version__ = (0, 9, 3)

README, HISTORY = "", ""
try:
    with open("README.rst") as f_readme:
        README = f_readme.read()
except:
    pass

try:
    with open("HISTORY.rst") as f_history:
        HISTORY = f_history.read()
except:
    pass

setup(
    name             = "minifold",
    version          = ".".join(["%s" % x for x in __version__]),
    description      = "minifold",
    long_description = "%s\n\n%s" % (README, HISTORY),
    long_description_content_type = "text/x-rst",
    author           = "Marc-Olivier Buob",
    author_email     = "marc-olivier.buob@nokia-bell-labs.com",
    url              = "http://github.com/nokia/minifold",
    license          = "BSD-3",
    packages         = find_packages(),
    package_dir      = {"minifold" : "minifold"},
    python_requires  = ">=3",
    requires         = ["typing"],
    test_suite       = "tests",
)
