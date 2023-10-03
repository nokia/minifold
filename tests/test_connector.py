#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import sys
from minifold.connector import Connector
from minifold.log import Log

Log.enable_print = True

if sys.version_info >= (3, 6):
    def test_subclasses():
        assert Connector.subclasses
        n = len(Connector.subclasses)
        if n == 0:
            from minifold.entries_connector import EntriesConnector
            assert len(Connector.subclasses) == 1
            _ = EntriesConnector([])
