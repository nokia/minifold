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

from pprint     import pformat
from .query     import Query
from .log       import Log

class Connector:
    enable_debug = False
    def __init__(self):
        """
        Constructor.
        """
        pass

    def query(self, query :Query) -> list:
        """
        Method called when this Connector handle an input Query.
        Args:
            query: The handled query.
        Returns:
            The list of entries matching the input Query.
        """
        if Connector.enable_debug:
            Log.debug("%r: --> %s" % (self, q))
        # This method must be overloaded by populating entries
        entries = list()
        return self.answer(query, entries)

    def attributes(self, object :str) -> set:
        """
        List available attributes related to a given object.
        Args:
            object: A string identifying an object.
        Returns:
            The set of available attributes for object.
        """
        # Must be overwritten in child class if reshape_entries is needed
        raise NotImplemented

    def reshape_entries(self, query :Query, entries :list) -> list:
        """
        Reshape entries returned by self.query() before calling self.answer().
        This method should only be called if the Connector only support a subset
        of Query operators among {SELECT, WHERE, LIMIT, OFFSET}
        Args:
            query: The handled Query instance.
            entries: The list of raw entries fetched so far, corresponding to
                SELECT * FROM foo LIMIT n
                where n >= query.limit
        """
        max_attributes = self.attributes(query)
        attributes = set(query.attributes) & max_attributes if query.attributes else max_attributes

        ret = list()
        for entry in entries[query.offset:]:
            # LIMIT
            if len(ret) == query.limit:
                break

            # WHERE
            if query.filters is None or query.filters.match(entry):
                # SELECT
                entry = {k : v for (k, v) in entry.items() if k in attributes}
                missing_attributes = set(attributes) - set(entry.keys())
                for k in missing_attributes:
                    entry[k] = None

                ret.append(entry)
        return ret

    def answer(self, query :Query, ret):
        """
        Method traversed when this Connector is ready to answer to a given Query.
        Args:
            query: The related Query instance.
            ret: The corresponding result.
        """
        if Connector.enable_debug:
            Log.debug("%r: <-- %s\n%s" % (
                self,
                query,
                pformat(ret)
            ))
        return ret
