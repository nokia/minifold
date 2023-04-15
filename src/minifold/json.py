#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import codecs, json
from .entries_connector import EntriesConnector

def identity(x: object) -> list:
    """
    Identity function.

    Args:
        x (object): An arbitrary object.

    Returns:
        The ``x`` object.
    """
    return x

def load_json_from_str(json_data: str, extract_json: callable = identity) -> list:
    """
    Loads minifold from a JSON string.

    Args:
        json_data (str): The JSON data.
        extract_json (callable): A function that reprocesses the python structure
            resulting from the JSON to produce a list of minifold entries.
            Defaults to :py:func:`identity`.

    Returns:
        A list of minifold entries.

    """
    assert isinstance(json_data, str)
    entries = extract_json(json.loads(json_data))
    assert isinstance(entries, list), f"Minifold expects a list of dict, got {type(entries)}"
    return entries

def load_json_from_file(json_filename: str, extract_json: callable = identity) -> list:
    """
    Loads minifold from a JSON file.

    Args:
        json_filename (str): The path to a JSON file.
        extract_json (callable): A function that reprocesses the python structure
            resulting from the JSON to produce a list of minifold entries.
            Defaults to :py:func:`identity`.

    Returns:
        A list of minifold entries.
    """
    with codecs.open(json_filename, encoding = "utf8") as f_json:
        entries = load_json_from_str(f_json.read(), extract_json)
    return entries

class JsonConnector(EntriesConnector):
    """
    The :py:class:`JsonConnector` class is a gateway to a JSON string.
    """
    def __init__(self, json_data: str, extract_json: callable = identity):
        """
        Constructor.

        Args:
            json_data: A JSON string.
            extract_json: A function that converts the JSON data to a list
                of minifold entries. Defaults to :py:func:`identity`.
        """
        entries = load_json_from_str(json_data, extract_json)
        assert isinstance(entries, list)
        super().__init__(entries)

class JsonFileConnector(JsonConnector):
    """
    The :py:class:`JsonConnector` class is a gateway to a JSON file.
    """
    def __init__(self, json_filename: str, extract_json: callable = identity):
        """
        Constructor.

        Args:
            json_filename: The path of the input JSON file.
            extract_json: A function that converts the JSON data to a list
                of minifold entries. Defaults to :py:func:`identity`.
        """
        with codecs.open(json_filename, encoding = "utf8") as f_json:
            super().__init__(f_json.read(), extract_json)

    # TODO: For the moment we only support ACTION_READ queries,
    # but this could be extended
