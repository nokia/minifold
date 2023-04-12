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
    """
    The :py:class:`Connector` class is the base class of most of classes involved in
    minifold.

    A minifold query plan is a hierarchy of :py:class:`Connector` instances.
    Running a query consists in sending a :py:class:`Query` instance to the root
    :py:class:`Connector` instance of the query plan.
    Then, each :py:class:`Connector` (possibly alters) and forwards
    the query to its children.
    The leaves of the query plan are :py:class:`Connector` are gateways allowing
    to fetch data from a remote or local data source.
    A read query returns the entries matched by the input minifold query (if any)
    to the parent node. Iteratively, the entries reach the root node of the query plan.

    As a result, once the hierarchy of the query plan is ready, the only relevant
    entry point is the root :py:class:`Connector` instance.
    """
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

        # https://stackoverflow.com/questions/5189232/how-to-auto-register-a-class-when-its-defined
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
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

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
        Lists available attributes related to a given collection of object
        stored in this :py:class:`Connector` instance.

        Args:
            object: The name of the collection of entries. The supported objects
                (if any) are specified in the specialized connector. If the
                connector only manages a single object collection, you may
                pass ``None``.

        Returns:
            The set of available attributes for ``object``.
        """
        # Must be overwritten in child class if reshape_entries is needed
        raise NotImplemented

    def reshape_entries(self, query :Query, entries :list) -> list:
        """
        Reshapes entries returned by :py:meth:`self.query` before calling
        :py:meth:`self.answer`.

        This method should only be called if the Connector only support a subset
        of query operators among ``{SELECT, WHERE, LIMIT, OFFSET}`` in SQL.

        Args:
            query: The handled Query instance.
            entries: The list of raw entries fetched so far, corresponding to
                ``SELECT * FROM foo LIMIT n WHERE n >= query.limit``.

        Returns:
            The reshaped entries.
        """
        max_attributes = self.attributes(query.object)
        attributes = (
            set(query.attributes) & max_attributes if query.attributes
            else max_attributes
        )

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

    def answer(self, query: Query, ret):
        """
        Method traversed when this :py:class:`Connector` is ready to
        answer to a given :py:class:`Query`.

        This method is used in the child classes to trace entries in
        the (complex) query plans.

        Args:
            query: The related :py:class:`Query` instance.
            ret: The corresponding results.
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
