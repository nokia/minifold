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

import codecs, json, os, traceback
from minifold.entries_connector import EntriesConnector

def identity(json_py) -> list:
    # Minifold expects a list of dict, so if you are looking
    # for a specific part of the json file, this callback
    # is an opportunity to extract the data of interests.
    return json_py

def load_json_from_str(json_data :str, extract_json = identity) -> list:
    assert isinstance(json_data, str)
    entries = extract_json(json.loads(json_data))
    assert isinstance(entries, list), "Minifold expects a list of dict, got %s" % type(entries)
    return entries

def load_json_from_file(json_filename :str, extract_json = identity) -> list:
    entries = None
    with codecs.open(json_filename, encoding = "utf8") as f_json:
        entries = load_json_from_str(f_json.read(), extract_json)
    return entries

class JsonConnector(EntriesConnector):
    def __init__(self, json_data :str, extract_json = identity):
        entries = load_json_from_str(json_data, extract_json)
        assert isinstance(entries, list)
        super().__init__(entries)

class JsonFileConnector(JsonConnector):
    def __init__(self, json_filename :str, extract_json = identity):
        with codecs.open(json_filename, encoding = "utf8") as f_json:
            super().__init__(f_json.read(), extract_json)
    # For the moment we only support ACTION_READ queries,
    # but this could be extended
