#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob, Dylan Sellar"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"


class ForEachFilter():
    def __init__(self, attribute_name: str, map_filter: dict):
        self.attribute_name = attribute_name
        self.map_filter = map_filter

    def match_filters(self, sub_entry):
        for attribute, filt in self.map_filter.items():
            if attribute in sub_entry.keys():
                if not filt(sub_entry[attribute]):
                    return False
        return True

    def __call__(self, entry: dict) -> bool:
        sub_entries = entry.get(self.attribute_name)

        if not sub_entries:
            return True

        entry[self.attribute_name] = [
            sub_entry \
            for sub_entry in sub_entries \
            if self.match_filters(sub_entry)
        ]

        return True

def for_each_sub_entry(entry, attribute :str, map_lambda :dict) -> dict:
    entry[attribute] = [
        {
              k : map_lambda[k](v) if k in map_lambda.keys() else v for k, v in sub_entry.items()
        } for sub_entry in entry[attribute]
    ]
    return entry

