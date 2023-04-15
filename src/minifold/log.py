#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import sys
from pprint import pformat

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3

# Shell colors
DEFAULT = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
PINK = 5
CYAN = 6
GRAY = 7

# Shell style
BOLD = 1
UNDERLINED = 4
BLINKING = 5
HIGHLIGHTED = 7

class Log:
    """
    The :py:class:`Log` enables logging in Minifold.

    Example:
        >>> Log.enable_print = True
        >>> Log.info("hello")
    """
    enable_print = False  # Set this variable to True to enable logging.
    with_color = True
    log_level = 0

    message_header = {
        DEBUG: "DEBUG",
        INFO: "INFO",
        WARNING: "WARNING",
        ERROR: "ERROR",
    }

    message_color = {
        DEBUG: CYAN,
        INFO: GREEN,
        WARNING: YELLOW,
        ERROR: RED,
    }

    @staticmethod
    def start_style(
        fg_color: int = None,
        bg_color: int = None,
        styles: list = None
    ) -> str:
        """
        Crafts a shell escape sequence to start a style.

        Args:
            fg_color (int): The integer identifying the foreground color to be used.
                _Example:_ ``GREEN``.
            bg_color (int): The integer identifying the background color to be used.
                _Example:_ ``PINK``.
            styles (list) A list of extra styles.
                _Example:_ ``[UNDERLINED, BLINKING]``.

        Returns:
            The corresponding shell string.
        """
        styling = list()
        if fg_color:
            styling.append("3%d" % fg_color)
        if bg_color:
            styling.append("4%d" % bg_color)
        if styles:
            styling += styles
        return "\033[%sm" % ";".join(styling) if styling else ""

    @staticmethod
    def default_style() -> str:
        """
        Crafts a shell escape sequence to set the default style
        """
        return "\033[0m"

    @classmethod
    def print(cls, message_type: int, message: str, file = sys.stderr):
        """
        Internal method, used to orints a message with a custom header and style.

        Args:
            message_type (int): A value in ``INFO``, ``DEBUG``, ``WARNING``, ``ERROR``.
            message (str): The message to log.
            file: The output stream. Defaults to ``sys.stderr``.
        """
        if cls.enable_print and message_type >= cls.log_level:
            color = cls.message_color[message_type]
            header = cls.message_header[message_type]
            print(
                "%(start_style)s%(message)s%(end_style)s" % {
                    "start_style" : cls.start_style(fg_color = color),
                    "message"     : " ".join([
                            header,
                            message if isinstance(message, str) else pformat(message)
                        ]),
                    "end_style"   : cls.default_style()
                },
                file = file
            )

    @classmethod
    def debug(cls, s: str):
        """
        Logs a debug message.

        Args:
            cls (Log): The :py:class:`Log` class.
            s (str): The string to log.
        """
        cls.print(DEBUG, s)

    @classmethod
    def info(cls, s: str):
        """
        Logs an info message.

        Args:
            cls (Log): The :py:class:`Log` class.
            s (str): The string to log.
        """
        cls.print(INFO, s)

    @classmethod
    def warning(cls, s: str):
        """
        Logs a warning message.

        Args:
            cls (Log): The :py:class:`Log` class.
            s (str): The string to log.
        """
        cls.print(WARNING, s)

    @classmethod
    def error(cls, s: str):
        """
        Logs an error message.

        Args:
            cls (Log): The :py:class:`Log` class.
            s (str): The string to log.
        """
        cls.print(ERROR, s)
