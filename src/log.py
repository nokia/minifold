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

import sys
from pprint import pformat

DEBUG   = 0
INFO    = 1
WARNING = 2
ERROR   = 3

# Shell colors
DEFAULT = 0
RED     = 1
GREEN   = 2
YELLOW  = 3
BLUE    = 4
PINK    = 5
CYAN    = 6
GRAY    = 7

# Shell style
DEFAULT     = 0
BOLD        = 1
UNDERLINED  = 4
BLINKING    = 5
HIGHLIGHTED = 7

class Log:
    enable_print = False

    # TODO: The following static paramaters should be load from ~/.minifoldrc
    # TODO: dark / light colors
    with_color   = True
    log_level    = 0

    message_header = {
        DEBUG   : "DEBUG",
        INFO    : "INFO",
        WARNING : "WARNING",
        ERROR   : "ERROR",
    }

    message_color = {
        DEBUG   : CYAN,
        INFO    : GREEN,
        WARNING : YELLOW,
        ERROR   : RED,
    }

    @staticmethod
    def start_style(
        fg_color :int = None,
        bg_color :int = None,
        styles :list = list()
    ) -> str:
        styling = list()
        if fg_color != None: styling.append("3%d" % fg_color)
        if bg_color != None: styling.append("4%d" % bg_color)
        if styles: styling += styles
        return "\033[%sm" % ";".join(styling) if styling else ""

    @staticmethod
    def default_style() -> str:
        return "\033[0m"

    @classmethod
    def print(cls, message_type :int, message :str, file = sys.stderr):
        if cls.enable_print and message_type >= cls.log_level:
            color  = cls.message_color[message_type]
            header = cls.message_header[message_type]
            print(
                "%(start_style)s%(message)s%(end_style)s" % {
                    "start_style" : cls.start_style(fg_color = color),
                    "message"     : " ".join([header, message if isinstance(message, str) else pformat(message)]),
                    "end_style"   : cls.default_style()
                },
                file = file
            )

    @classmethod
    def debug(cls, s): cls.print(DEBUG, s)

    @classmethod
    def info(cls, s): cls.print(INFO, s)

    @classmethod
    def warning(cls, s): cls.print(WARNING, s)

    @classmethod
    def error(cls, s): cls.print(ERROR, s)

