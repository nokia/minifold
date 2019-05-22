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

from copy import deepcopy
from typing import List

ACTION_CREATE = 0
ACTION_READ   = 1
ACTION_UPDATE = 2
ACTION_DELETE = 3

SORT_ASC  = True
SORT_DESC = False

def action_to_str(action) -> str:
    if   action == ACTION_CREATE: return "INSERT"
    elif action == ACTION_READ  : return "SELECT"
    elif action == ACTION_UPDATE: return "UPDATE"
    elif action == ACTION_DELETE: return "DELETE"
    else: raise RuntimeError("action_to_str: invalid action %s" % action)

class Query:
    def __init__(self, action = ACTION_READ, object = "", attributes :List = list(), filters :List = None, offset = None, limit = None, sort_by = dict()):
        self.m_action = action
        self.m_object = object
        self.m_attributes = list(attributes)
        self.m_filters = filters

        # NOTE/TODO: the following specifiers are not supported by all the connectors
        self.m_offset = offset
        self.m_limit = limit
        self.m_sort_by = sort_by

    def copy(self):
        return deepcopy(self)

    @property
    def action(self) -> int:
        return self.m_action

    @action.setter
    def action(self, value :int):
        self.m_action = value

    @property
    def attributes(self) -> list:
        return self.m_attributes

    @attributes.setter
    def attributes(self, value :list):
        self.m_attributes = value

    @property
    def filters(self):
        return self.m_filters

    @filters.setter
    def filters(self, value):
        self.m_filters = value

    @property
    def limit(self) -> int:
        return self.m_limit

    @limit.setter
    def limit(self, value :int):
        self.m_limit = value

    @property
    def offset(self) -> int:
        return self.m_offset

    @offset.setter
    def offset(self, value :int):
        self.m_offset = value

    @property
    def sort_by(self) -> dict:
        return self.m_sort_by

    @sort_by.setter
    def sort_by(self, value :dict):
        self.m_sort_by = value

    @property
    def object(self) -> str:
        return self.m_object

    def __str__(self) -> str:
        return "%(action)s%(attributes)s%(object)s%(filters)s%(limit)s%(offset)s%(sort_by)s" % {
            "action"     : action_to_str(self.action),
            "attributes" : " %s" % ", ".join(sorted(set(self.attributes))) if len(self.attributes) > 0 else " *",
            "object"     : " FROM %s" % self.object   if self.object  else "",
            "filters"    : " WHERE %s" % self.filters if self.filters else "",
            "limit"      : " LIMIT %s" % self.limit   if self.limit   else "",
            "offset"     : " OFFSET %s" % self.offset if self.offset  else "",
            "sort_by"    : " SORT BY %s" % ", ".join([
                    "%s %s" % (
                        attribute,
                        "ASC" if sort_asc == SORT_ASC else "DESC"
                    ) for attribute, sort_asc in self.sort_by.items()
                ]) if self.sort_by else "",
        }

