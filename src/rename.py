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

from copy                   import deepcopy

from .binary_predicate      import BinaryPredicate
from .connector             import Connector
from .query                 import Query

def rename_list(l :list, mapping :dict) -> list:
    for i, value in enumerate(l):
        try:
            l[i] = mapping[value]
        except KeyError as e:
            #l[i] = None
            pass # see test_dblp.py
    return l

def rename_key(d :dict, old_key :str, new_key :str) -> dict:
    try:
        d[new_key] = d.pop(old_key)
    except KeyError:
        pass
    return d

def rename_entry(d :dict, mapping :dict) -> dict:
    for old_key, new_key in mapping.items():
        rename_key(d, old_key, new_key)
    return d

def rename(mapping :dict, entries :list) -> list:
    for entry in entries:
        rename_entry(entry, mapping)
    return entries

def rename_filters(filters, mapping :dict):
    if filters == None or isinstance(filters, int) or isinstance(filters, tuple):
        pass
    elif isinstance(filters, str):
        try:
            filters = mapping[filters]
        except KeyError:
            pass
    elif isinstance(filters, BinaryPredicate):
        filters.m_left  = rename_filters(filters.left,  mapping)
        filters.m_right = rename_filters(filters.right, mapping)
    else:
        raise RuntimeError("rename_filters: unsupported type %s: filters = %s" % (type(filters), filters))
    return filters

def rename_sort_by(sort_by :dict, mapping :dict) -> dict:
    return {mapping.get(attribute, attribute) : sort_asc for attribute, sort_asc in sort_by.items()} if sort_by else dict()

def rename_query(q :Query, mapping :dict) -> Query:
    q_renamed = q
    rename_list(q_renamed.attributes, mapping)
    rename_filters(q_renamed.filters, mapping)
    q.sort_by = rename_sort_by(q_renamed.sort_by, mapping)
    return q_renamed

def reverse_dict(d :dict) -> dict:
    ret = dict()
    for k,v in d.items():
        ret[v] = k
    return ret

class RenameConnector(Connector):
    def __init__(self, mapping :dict = {}, child = None):
        super().__init__()
        self.m_map_rq = mapping
        self.m_map_qr = reverse_dict(mapping)
        self.m_child  = child

    def attributes(self, object :str) -> set:
        return {self.map_rq.get(attribute, attribute) for attribute in  self.m_child.attributes(object)}

    def query(self, q :Query) -> list:
        super().query(q)
        assert self.child != None
        q_renamed = rename_query(deepcopy(q), self.map_qr)
        return self.answer(
            q,
            rename(
                self.map_rq,
                self.child.query(q_renamed)
            )
        )

    @property
    def child(self):
        return self.m_child

    @property
    def map_qr(self):
        return self.m_map_qr

    @property
    def map_rq(self):
        return self.m_map_rq


