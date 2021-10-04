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

import sys
from pprint     import pformat
from .query     import Query
from .log       import Log

class Connector:
    trace_queries = False
    trace_entries = False
    trace_only_keys = False

    def __init__(self):
        """
        Constructor.
        """
        pass

    if sys.version_info >= (3, 6):
        subclasses = dict()

        #https://stackoverflow.com/questions/5189232/how-to-auto-register-a-class-when-its-defined
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            name = repr(cls).split("'")[1]
            Connector.subclasses[name] = cls

        @staticmethod
        def get_class(name :str):
            cls = Connector.subclasses.get(name)
            if not cls:
                raise RuntimeError(
                    "Invalid connector type [%s]. Known types are:\n%s\n" % (
                        name,
                        "\n\t".join([str(name) for name in subclasses.keys()])
                    )
                )
            return cls

    def query(self, query :Query) -> list:
        """
        Method called when this Connector handle an input Query.
        Args:
            query: The handled query.
        Returns:
            The list of entries matching the input Query.
        """
        if Connector.trace_queries:
            Log.debug("%r: --> %s" % (self, query))
        # This method must be overloaded in child classes as follows:
        # super().query(query)
        # entries = [ ... ]
        # return self.answer(query, entries)
        return list()

    def attributes(self, object :str) -> set:
        """
        List available attributes related to a given object.
        Args:
            object: The name of the object
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
        max_attributes = self.attributes(query.object)
        attributes = set(query.attributes) & max_attributes if query.attributes else max_attributes

        ret = list()
        for entry in entries[query.offset:]:
            # LIMIT
            if len(ret) == query.limit:
                break

            # WHERE
            if query.filters is None or query.filters(entry):
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
        if Connector.trace_entries or Connector.trace_only_keys:
            if isinstance(ret, list) and Connector.trace_only_keys and len(ret) > 0:
                entry = ret[0]
                message = "Forwarding %d entries, keys = {%s}" % (
                    len(ret),
                    ", ".join(entry.keys())
                )
            else:
                message = pformat(ret)
            Log.debug("%r: <-- %s\n%s" % (self, query, message))
        return ret
