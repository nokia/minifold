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

from .connector             import Connector
from .query                 import Query, ACTION_READ

# The following schema summarizes the different joins
# http://4.bp.blogspot.com/-_HsHikmChBI/VmQGJjLKgyI/AAAAAAAAEPw/JaLnV0bsbEo/s1600/sql%2Bjoins%2Bguide%2Band%2Bsyntax.jpg

INNER_JOIN      = 1 # Returns matching records
LEFT_JOIN       = 2 # Returns left entries + matching right entries (=> right attributes may be None)
RIGHT_JOIN      = 3 # Returns right entries + matching left entries (=> left attributes may be None)
FULL_OUTER_JOIN = 4 # Returns left and right entries while merging matching entries

def merge_dict(l :dict, r :dict) -> dict:
    ret = l.copy()
    ret.update(r)
    return ret

def join_mode_to_string(mode :int) -> str:
    if   mode == INNER_JOIN:      return "INNER JOIN"
    elif mode == LEFT_JOIN:       return "LEFT JOIN"
    elif mode == RIGHT_JOIN:      return "RIGHT JOIN"
    elif mode == FULL_OUTER_JOIN: return "FULL OUTER JOIN"
    return "?"

def are_joined_if(l :dict, r :dict, f) -> bool:
    try:
        return f(l, r)
    except KeyError as e:
        raise RuntimeError("Cannot join\n\tl = %r\n\tr = %r\n%s" % (l, r, e))

def inner_join_if(l_entries :list, r_entries :list, f, match_once = True, merge = merge_dict) -> list:
    ret = list()
    for l in l_entries:
        for r in r_entries:
            if are_joined_if(l, r, f):
                ret.append(merge(l, r))
                if match_once: break
    return ret

def left_join_if(l_entries :list, r_entries :list, f, match_once = True, merge = merge_dict) -> list:
    ret = list()
    if len(r_entries) > 0:
        for l in l_entries:
            joined = False
            for r in r_entries:
                if are_joined_if(l, r, f):
                    joined = True
                    ret.append(merge(l, r))
                    if match_once: break
            if joined == False:
                entry = l
                missing_keys = set(r.keys()) - set(l.keys())
                for k in missing_keys:
                    entry[k] = None
                ret.append(entry)
    else:
        ret = l_entries
    return ret

def right_join_if(l_entries :list, r_entries :list, f, match_once = True) -> list:
    return left_join_if(r_entries, l_entries, lambda l,r: f(r,l), match_once)

def full_outer_join_if(l_entries :list, r_entries :list, f, match_once = True) -> list:
    # Get every left entries (joinable or not)
    ret = left_join_if(l_entries, r_entries, f, match_once)

    # Retrieve left keys
    l_keys = set()
    for l in l_entries:
        l_keys |= {k for k in l.keys()}

    # Get missing right entries
    for r in r_entries:
        joined = False
        for l in l_entries:
            if are_joined_if(l, r, f):
                joined = True
                break

        if joined == False:
            entry = r
            missing_keys = set(l_keys) - set(r.keys())
            for k in missing_keys:
                entry[k] = None
            ret.append(entry)

    return ret

class JoinIfConnector(Connector):
    def __init__(self, left :Connector, right :Connector, join_if, mode :int = INNER_JOIN):
        super().__init__()
        self.m_left = left
        self.m_right = right
        self.m_join_if = join_if
        self.m_left_entries = list()
        self.m_right_entries = list()
        self.m_mode = mode

    def attributes(self, object :str):
        return self.m_left.attributes(object) \
             | self.m_right.attributes(object)

    def query(self, query :Query) -> list:
        super().query(query)
        self.m_left_entries.clear()
        self.m_right_entries.clear()
        self.m_left_entries = self.left.query(query)
        self.m_right_entries = self.right.query(query)
        if   self.m_mode == INNER_JOIN:
            entries = inner_join_if(self.m_left_entries, self.m_right_entries, self.m_join_if)
        elif self.m_mode == LEFT_JOIN:
            entries = left_join_if(self.m_left_entries, self.m_right_entries, self.m_join_if)
        elif self.m_mode == RIGHT_JOIN:
            entries = right_join_if(self.m_left_entries, self.m_right_entries, self.m_join_if)
        elif self.m_mode == FULL_OUTER_JOIN:
            entries = full_outer_join_if(self.m_left_entries, self.m_right_entries, self.m_join_if)
        else:
            raise ValueError("JoinIfConnector::answer: Invalid mode %s:" % self.m_mode)
        return self.answer(query, entries)

    @property
    def mode(self):
        return self.m_mode

    @property
    def left(self):
        return self.m_left

    @property
    def right(self):
        return self.m_right

    @property
    def join_if(self):
        return self.m_join_if

