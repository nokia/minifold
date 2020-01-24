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

import operator
from .binary_predicate  import BinaryPredicate
from .connector         import Connector
from .log               import Log
from .query             import ACTION_READ, Query
from .scholar           import ScholarArticle, ScholarQuerier, ScholarSettings, SearchScholarQuery

class GoogleScholarConnector(Connector):
    def __init__(self, citation_format :str = ScholarSettings.CITFORM_BIBTEX):
        # Prepare the querier
        settings = ScholarSettings()
        settings.set_citation_format(citation_format)
        self.querier = ScholarQuerier()
        self.querier.apply_settings(settings)

    def attributes(self, object :str) -> set:
        if object == "publication":
            article = ScholarArticle()
            return set(article.keys())
        elif object == "cluster":
            raise RuntimeError("Object %s is not yet supported" % object)
        else:
            raise RuntimeError("Invalid object %s" % object)

    @staticmethod
    def filter_to_scholar(p :BinaryPredicate, gs_query :SearchScholarQuery):
        if p.operator == operator.__and__:
            GoogleScholarConnector.filter_to_scholar(p.left, gs_query)
            GoogleScholarConnector.filter_to_scholar(p.right, gs_query)
            return

        if isinstance(p.left,  BinaryPredicate) \
        or isinstance(p.right, BinaryPredicate):
            raise RuntimeError("Invalid clause %s" % p)

        attr = p.left
        value = p.right
        if not isinstance(attr, str):
            raise RuntimeError("Invalid left operand %s" % p)

        if attr == "author":
            if p.operator == operator.__eq__:
                gs_query.set_author(value)
            else:
                raise RuntimeError("Invalid operator %s" % p)
        elif attr == "words":
            if p.operator == operator.__eq__ or p.operator == operator.__ge__:
                gs_query.set_words(options.allw)      # All of these words must appear
            elif p.operator == operator.__le__:
                gs_query.set_words_some(options.some) # Some of these words must appear
            elif p.operator == operator.__ne__:
                gs_query.set_words_none(options.none) # None of these words must appear
            else:
                raise RuntimeError("Invalid operator %s" % p)
        elif attr == "phrase":
            Log.warning("GoogleScholarConnector: filtering on %s not yet implemented" % attr)
            #gs_query.set_phrase(options.phrase)
            pass
        elif attr == "doc_type":
            Log.warning("GoogleScholarConnector: filtering on %s not yet implemented" % attr)
            # NOT YET IMPLEMENTED
            # gs_query.set_include_patents(False)
            # gs_query.set_include_citations(False)
            pass
        elif attr == "year":
            assert isinstance(value, int)
            (start, end) = gs_query.timeframe
            if p.operator == operator.__eq__:
                start = max(start, value) if start else value
                end   = min(end, value) if end else value
            elif p.operator == operator.__le__:
                end = min(end, value)     if end else value
            elif p.operator == operator.__lt__:
                end = min(end, value - 1) if end else value
            elif p.operator == operator.__ge__:
                start = max(start, value) if start else value
            elif p.operator == operator.__gt__:
                start = max(start, value + 1) if start else value
            else:
                raise RuntimeError("Invalid operator %s" % p)
            print("start = %r end = %r" % (start, end))
            if start is not None and end is not None and end < start:
                raise RuntimeError("Invalid range of date")
            gs_query.set_timeframe(start, end)
        elif attr == "publication":
            if p.operator == operator.__eq__:
                gs_query.set_pub(value)
            else:
                raise RuntimeError("Invalid operator %s" % p)

    def query(self, query :Query) -> list:
        super().query(query)
        ret = None
        if query.action != ACTION_READ:
            raise RuntimeError("Action not supported" % query.action)
        if not isinstance(query.filters, BinaryPredicate):
            raise RuntimeError("Invalid filter" % query.filters)

        if query.object == "cluster":
            gs_query = ClusterScholarQuery(cluster=options.cluster_id)
        elif query.object == "publication" or not query.object:
            gs_query = SearchScholarQuery()
            GoogleScholarConnector.filter_to_scholar(query.filters, gs_query)
        else:
            raise RuntimeError("Invalid object %r" % query.object)

        # Craft the query
        if query.limit is not None:
            gs_query.set_num_page_results(min(query.limit, ScholarConf.MAX_PAGE_RESULTS))

        # Send the query
        self.querier.send_query(gs_query)

        # Extract results
        ret = [{k : v[0] for (k, v) in article.attrs.items()} for article in self.querier.articles]
        return self.answer(query, ret)
