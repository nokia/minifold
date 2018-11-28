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

import json, os, traceback
from minifold.entries_connector import EntriesConnector
from minifold.log               import Log

def load_json_from_str(json_data :str) -> list:
    return json.loads(json_data)

def load_json_from_file(json_filename :str) -> list:
    entries = None
    try:
        with open(json_filename, "r") as f_json:
            entries = load_json_from_str(f_json.read())
    except Exception as e:
        Log.error(traceback.print_exc())
    return entries

class JsonConnector(EntriesConnector):
    def __init__(self, json_data :str):
        super().__init__(load_json_from_str(json_data))

class JsonFileConnector(JsonConnector):
    def __init__(self, json_filename :str):
        super().__init__(load_json_from_file(json_filename))
    # For the moment we only support ACTION_READ queries,
    # but this could be extended
