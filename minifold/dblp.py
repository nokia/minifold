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

# API specs:
#   https://wiki.inria.fr/lincs/Dblp-api
#
# Examples:
#   http://dblp.dagstuhl.de/search/publ/api?q=fabien-mathieu&h=500&format=json
#   http://dblp.dagstuhl.de/search/publ/api?q=fabien-mathieu%20year:2014&h=500&format=json

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    raise ImportError("DblpConnector requires python3-urllib3: please run: apt-get install python3-urllib3")

import json, urllib.parse

from .binary_predicate      import BinaryPredicate
from .doc_type              import DocType
from .log                   import Log
from .strings               import remove_accents, to_canonic_fullname
from .query                 import Query, ACTION_READ

# Default DBLP API queried.
DBLP_API_URL = "http://dblp.dagstuhl.de/search"

# Maps DBLP ontology to our ontology
DBLP_ALIASES = {
    "type"    : "dblp_doc_type",
    "venue"   : "conference",
    "url"     : "dblp_url",
}

class DblpConnector:
    def __init__(self, map_dblp_name = {}, dblp_api_url = DBLP_API_URL):
        self.m_api_url = dblp_api_url
        self.m_format  = "json" # valid values are: "xml", "json", and "jsonp".
        self.m_map_dblp_name = map_dblp_name

    @property
    def api_url(self) -> str:
        return self.m_api_url

    @property
    def format(self) -> str:
        return self.m_format

    @property
    def map_dblp_name(self) -> str:
        return self.m_map_dblp_name

    @staticmethod
    def to_dblp_name(s :str, map_dblp_name = {}) -> str:
        try:
            ret = map_dblp_name[s]
        except KeyError:
            s = remove_accents(s)
            s = s.replace("ç", "c")
            words = s.lower().split()
            try:
                words.remove("")
            except ValueError:
                pass
            # a-b means that b must follows a
            # a_b means that both a and b must be found
            ret = "-".join(words)

        # $ corresponds to exact match
        # See: http://dblp.uni-trier.de/db/about/author.html
        return "%s$" % ret

    def binary_predicate_to_dblp(self, p :BinaryPredicate, result :dict):
        if p.operator == "&&":
            self.binary_predicate_to_dblp(p.left, result),
            self.binary_predicate_to_dblp(p.right, result)
            return

        if not isinstance(p.left, str):
            raise RuntimeError("binary_predicate_to_dblp: left operand (%r) of %s must be a string" % (p.left, p))

        if p.left in ["author", "authors", "researcher", "conference"]:
            if p.operator == "==":
                result["prefix"] = DblpConnector.to_dblp_name(p.right, self.map_dblp_name)
            else:
                raise RuntimeError("binary_predicate_to_dblp: unsupported operator (%s): %s" % (p.operator, p))
        else:
            if p.operator == "==" or p.operator == "~":
                result["suffix"] += "%20" + ("%s:%s" % (p.left, p.right))
            else:
                raise RuntimeError("binary_predicate_to_dblp: unsupported operator (%s): %s" % (p.operator, p))

    @staticmethod
    def to_doc_type(s :str) -> DocType:
        s = s.lower()
        if   s in ["conference and workshop papers", "conference or workshop"]:
            return DocType.ARTICLE
        #elif s == "????":
        #    return DocType.COMM
        elif s == "journal articles":
            return DocType.JOURNAL
        elif s == "informal publications":
            return DocType.REPORT
        elif s == "books and theses":
            return DocType.BOOKS_AND_THESES
        #elif s == "????":
        #    return DocType.HDR
        elif s == "editorship":
            return DocType.CHAPTER
        else:
            Log.warning("DblpConnector.to_doc_type: unknown type: %s" % s)
            return DocType.UNKNOWN

    @staticmethod
    def sanitize_entry(q :Query, entry :dict) -> dict:
        # TODO not clear if we should keep "doc_type"
        if (("doc_type" in q.attributes) and ("type" in entry.keys())) or (len(q.attributes) == 0 and q.object == "publication"):
            entry["doc_type"] = DblpConnector.to_doc_type(entry["type"])
        # TODO this should only be:
        if (("dblp_doc_type" in q.attributes) and ("type" in entry.keys())) or (len(q.attributes) == 0 and q.object == "publication"):
            entry["dblp_doc_type"] = DblpConnector.to_doc_type(entry["type"])

        if len(q.attributes) > 0:
            keys = set(entry.keys()) & set(q.attributes)
            entry = {k: entry[k] for k in keys}

        for k,v in entry.items():
            if isinstance(v, str):
                try:
                    entry[k] = int(v)
                except ValueError:
                    pass

        return entry

    @staticmethod
    def extract_entries(query :Query, results :list) -> list:
        entries = list()
        try:
            raw_entries = results["result"]["hits"]["hit"]
            for raw_entry in raw_entries:
                entry               = raw_entry["info"]
                entry["dblp_id"]    = int(raw_entry["@id"])
                entry["dblp_score"] = int(raw_entry["@score"])

                try:
                    entry["authors"] = entry.pop("authors")["author"]
                except KeyError:
                    pass

                # Unfortunately, DBLP seems unable to perform exact match search.
                # For example searching "francois-durand$" returns "Jean-François Durand"
                # when searching "François Durand". The following discards the
                # false positives.

                if query.object not in ["publication", "researcher", "conference"]:
                    authors = [to_canonic_fullname(author) for author in entry["authors"]]
                    if to_canonic_fullname(query.object) not in authors:
                        continue

                entries.append(entry)
        except KeyError: # occurs if 0 DBLP publication found
            pass
        return entries

    @staticmethod
    def sanitize_entries(q :Query, entries :list) -> list:
        return [DblpConnector.sanitize_entry(q, entry) for entry in entries]

    def query(self, q :Query) -> list:
        entries = list()
        if q.action == ACTION_READ:

            use_dblp_name = False
            object = ""
            if   q.object == "publication": object = "publ"
            elif q.object == "researcher":  object = "author"
            elif q.object == "conference":  object = "venue"
            else:
                # We assume that q.object is a DBLP id and that
                # we're looking for the corresponding publications.
                use_dblp_name = True
                object = "publ"

            search = {
                "prefix" : "" if use_dblp_name == False else DblpConnector.to_dblp_name(q.object, self.map_dblp_name),
                "suffix" : ""
            }

            if q.filters != None:
                self.binary_predicate_to_dblp(q.filters, search)

            # DBLP API does not allow to select specific attributes,
            # define filters, etc. It only returns publications matching
            # a searched string.
            url_options = list()
            url_options.append("%s%s" % (search["prefix"], search["suffix"]))
            if q.limit  != None: url_options.append("h=%s" % q.limit)
            if q.offset != None: url_options.append("f=%s" % q.offset)
            url_options.append("format=%s" % self.format)

            q_dblp = "%(server)s/%(object)s/api?q=%(query)s" % {
                "server" : self.api_url,
                "object" : object,
                "query"  : "&".join(url_options)
            }

            Log.info("--> DBLP: %s (%s)" % (q_dblp, q))
            http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=2.0))
            reply = http.request("GET", q_dblp)

            if reply.status == 200:
                if self.m_format == "json":
                    result = json.loads(reply.data.decode("utf-8"))
                else:
                    raise RuntimeError("Format not implemented: %s" % self.m_format)
            else:
                raise RuntimeError("Cannot get reply from %s" % self.m_api_url)

        entries = DblpConnector.extract_entries(q, result)
        return self.answer(DblpConnector.sanitize_entries(q, entries))

    def answer(self, entries :list) -> list:
        return entries
