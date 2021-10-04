#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob and Fabien Mathieu"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

# 1) API specs:
#   https://wiki.inria.fr/lincs/Dblp-api
#
# Examples:
#   https://dblp.dagstuhl.de/search/publ/api?q=fabien-mathieu&h=500&format=json
#   https://dblp.dagstuhl.de/search/publ/api?q=fabien-mathieu%20year:2014&h=500&format=json
#
# 2) By default DBLP only returns up to 30 records. See:
#   https://dblp.org/faq/How+to+use+the+dblp+search+API.html
# The default limit in DblpConnector is set to 9999.
#
# 3) It is possible to query a specific researcher using its DBLP-ID.
# The ID can be found by browsing the page related to a researcher.
#
# Example:
#   https://dblp.uni-trier.de/pers/hd/c/Chen:Chung_Shue
#   The DBLP ID can be obtained by clicking on the export bibliography icon.
#
# For the moment, only XML is supported by DBLP.
#   https://dblp.org/pid/30/1446.xml
#
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    raise ImportError("DblpConnector requires python3-urllib3: please run: apt-get install python3-urllib3")

try:
    import requests
except ImportError:
    raise ImportError("DblpConnector requires requests")


try:
    import xmltodict
except ImportError:
    raise ImportError("DblpConnector requires python3-xmltodict: please run: apt-get install python3-xmltodict")

import json, operator
from pprint import pformat

from .binary_predicate      import BinaryPredicate
from .connector             import Connector
from .doc_type              import DocType
from .log                   import Log
from .strings               import to_international_string, to_canonic_fullname as _to_canonic_fullname
from .query                 import Query, ACTION_READ

# Default queried DBLP API.
DBLP_API_URL = "https://dblp.dagstuhl.de"

# Maps DBLP ontology to our ontology.
DBLP_ALIASES = {
    "type"    : "dblp_doc_type",
    "venue"   : "conference",
    "url"     : "dblp_url",
}

def to_canonic_fullname(s) -> str:
    # DBLP may now returns {"@pid" : int, "text" : "Firstname Lastname"} instead of the author fullname.
    if isinstance(s, dict):
        s = s["text"]
    return _to_canonic_fullname(s)

class DblpConnector(Connector):
    def __init__(self, map_dblp_id = {}, map_dblp_name = {}, dblp_api_url = DBLP_API_URL):
        super().__init__()
        self.m_api_url = dblp_api_url
        assert not dblp_api_url.endswith("/search") and not dblp_api_url.endswith("/search/"), \
            "Invalid API URL [%s], remove '/search/' suffix" % dblp_api_url
        self.m_format  = "json" # valid values are: "xml", "json", and "jsonp".
        self.m_map_dblp_id = map_dblp_id
        self.m_map_dblp_name = map_dblp_name
        self.m_map_rev_name = {to_canonic_fullname(dblp_name) : name for (name, dblp_name) in map_dblp_name.items()}

    def attributes(self, object :str) -> set:
        return {"authors", "doc_type", "title", "type", "venue", "url", "year"} # Non exhaustive

    @property
    def api_url(self) -> str:
        return self.m_api_url

    @property
    def format(self) -> str:
        return self.m_format

    @property
    def map_dblp_name(self) -> str:
        return self.m_map_dblp_name

    @property
    def map_dblp_id(self) -> str:
        return self.m_map_dblp_id

    @staticmethod
    def to_dblp_name(s :str, map_dblp_name = {}) -> str:
        ret = map_dblp_name.get(s, s)
        s = to_international_string(s)
        words = s.lower().split()
        try:
            words.remove("")
        except ValueError:
            pass
        # a-b means that b must follows a
        # a_b means that both a and b must be found
        # $ corresponds to exact match
        # See: http://dblp.uni-trier.de/db/about/author.html
        ret = "-".join(words) + "$"

        return ret

    def get_dblp_name(self, s :str) -> str:
        return DblpConnector.to_dblp_name(s, self.map_dblp_name)

    def get_dblp_id(self, s :str) -> str:
        pid = self.m_map_dblp_id.get(s)
        return pid if pid else self.get_dblp_name(s)

    def binary_predicate_to_dblp(self, p :BinaryPredicate, result :dict):
        # Recursive call only supported for && clauses
        if p.operator == operator.__and__:
            self.binary_predicate_to_dblp(p.left, result),
            self.binary_predicate_to_dblp(p.right, result)
            return

        # Simple predicate. The left member must be a attribute name of the entry.
        if not isinstance(p.left, str):
            raise RuntimeError("binary_predicate_to_dblp: left operand (%r) of %s must be a string" % (p.left, p))

        if p.left in ["author", "authors", "researcher", "conference"]:
            # String attribute. Only "CONTAINS" and "==" are supported. "==" behaves like "CONTAINS"
            if p.operator == operator.__eq__ or p.operator == operator.__contains__:
                result["prefix"] = self.get_dblp_name(p.right)
            else:
                raise RuntimeError("binary_predicate_to_dblp: unsupported operator (%s): %s" % (p.operator, p))
        else:
            # Other attributes. Only "==" is supported.
            if p.operator == operator.__eq__:
                result["suffix"] += "%20" + ("%s:%s" % (p.left, p.right))
            else:
                raise RuntimeError("binary_predicate_to_dblp: unsupported operator (%s): %s" % (p.operator, p))

    @staticmethod
    def to_doc_type(s :str) -> DocType:
        s = s.lower()
        if   s in {
            "article", "conference and workshop papers", "conference or workshop",
            "incollection", "inproceedings", "proceedings"
        }:
            return DocType.ARTICLE
        #elif s == "????":
        #    return DocType.COMM
        elif s == "journal articles":
            return DocType.JOURNAL
        elif s in {"informal publications", "reference works"}:
            return DocType.REPORT
        elif s in {"phdthesis", "books and theses", "parts in books or collections"}:
            return DocType.BOOKS_AND_THESES
        #elif s == "????":
        #    return DocType.HDR
        elif s == "editorship":
            return DocType.CHAPTER
        else:
            Log.warning("DblpConnector.to_doc_type: unknown type: %s" % s)
            return DocType.UNKNOWN

    def reshape_entry(self, query :Query, entry :dict) -> dict:
        if "type" in entry.keys():
            doc_type = DblpConnector.to_doc_type(entry["type"])
            entry["doc_type"]      = doc_type # Compatible with Hal "doc_type" values.
            entry["dblp_doc_type"] = doc_type # To compare Hal and DBLP doc_types.

        if len(query.attributes) > 0:
            keys = set(entry.keys()) & set(query.attributes)
            entry = {k : entry[k] for k in keys}

        for (k, v) in entry.items():
            if isinstance(v, str):
                try:
                    entry[k] = int(v)
                except ValueError:
                    pass

        if "authors" in entry.keys():
            if isinstance(entry["authors"], (dict, str)):
                entry["authors"] = [entry["authors"]]

            # Fix author names having homonyms are not well-named (e.g
            # "Giovanni Pau 0001" instead of "Giovanni Pau").
            entry["authors"] = [
                to_canonic_fullname(author).rstrip(" 0123456789") for author in entry["authors"]
            ]

            # Convert DBLP names to our names if needed.
            entry["authors"] = [
                self.m_map_rev_name.get(_to_canonic_fullname(author), author) \
                for author in entry["authors"]
            ]

        return entry

    def extract_entries(self, query :Query, results :list) -> list:
        entries = list()
        # If the query is not a standard Dblp object, we are pulling a bibliography
        # of a researcher who is identified by query.object (PID or fullname)
        is_bib_query = query.object not in {"publication", "researcher", "conference"}
        canonic_fullname = to_canonic_fullname(self.get_dblp_name(query.object)).rstrip("$") if is_bib_query else None
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

                if is_bib_query:
                    # Unfortunately, DBLP seems unable to perform exact match search.
                    # For example searching "francois-durand$" returns "Jean-François
                    # Durand" publications.
                    # The following discards the false positives.
                    if isinstance(entry["authors"], str):
                        entry["authors"] = [entry["authors"]]

                    if canonic_fullname not in [
                        to_canonic_fullname(author) for author in entry["authors"]
                    ]:
                        #Log.warning("Ignoring %(title)s %(authors)s (homonym)" % entry)
                        continue

                entries.append(entry)
        except KeyError: # occurs if 0 DBLP publication found
            pass
        return entries

    def reshape_entries(self, query :Query, entries :list) -> list:
        return [self.reshape_entry(query, entry) for entry in entries]

    def query(self, query :Query) -> list:
        super().query(query)
        entries = list()
        if query.action == ACTION_READ:

            pid = None
            format = self.format
            object = ""
            url_options = list()
            if   query.object == "publication":
                object = "search/publ"
            elif query.object == "researcher":
                object = "search/author"
            elif query.object == "conference":
                object = "search/venue"
            else:
                fullname = query.object
                pid = self.map_dblp_id.get(fullname)
                dblp_name = self.get_dblp_name(fullname)
                object = "pid" if pid else "search/publ"
                # For the moment, DBLP only supports XML for pid-based queries.
                # https://dblp.org/pid/30/1446.xml
                if pid: format = "xml"
                else: url_options.append(dblp_name)

            if object == "pid":
                q_dblp = "%(server)s/%(object)s/%(pid)s.%(format)s" % {
                    "server" : self.api_url,
                    "object" : object,
                    "pid"    : pid,
                    "format" : format,
                }
            else:
                # WHERE
                if query.filters:
                    search = {
                        "prefix" : self.get_dblp_name(query.object),
                        "suffix" : ""
                    }
                    self.binary_predicate_to_dblp(query.filters, search)
                    url_options.append("%s%s" % (search["prefix"], search["suffix"]))

                # OFFSET and LIMIT
                url_options.append("h=%s" % query.limit if query.limit is not None else "h=9999")
                if query.offset:
                    url_options.append("f=%s" % query.offset)

                # Format of the result.
                url_options.append("format=%s" % format)
                q_dblp = "%(server)s/%(object)s/api?q=%(query)s" % {
                    "server" : self.api_url,
                    "object" : object,
                    "query"  : "&".join(url_options)
                }

            Log.info("--> DBLP: %s" % q_dblp)
            # http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=2.0))
            # reply = http.request("GET", q_dblp, retries = 5)
            reply = requests.get(q_dblp)

            if reply.status_code == 200:
                data = reply.content.decode("utf-8")
                if format == "json":
                    result = json.loads(data)
                    entries = self.extract_entries(query, result)
                elif format == "xml":
                    data = data.replace("<i>", "")
                    data = data.replace("</i>", "")
                    result = xmltodict.parse(data, dict_constructor=dict)
                    # N.B. There are two other keys of interests
                    # - "co" : coauthors
                    # - "person" : information about the researcher

                    def xml_to_entry(d :dict) -> dict:
                        publication_type = next(iter(d.keys()))
                        entry = d[publication_type]
                        entry["type"] = publication_type
                        key = \
                            "author" if "author" in entry.keys() else \
                            "editor" if "editor" in entry.keys() else \
                            None
                        if key:
                            # Sometimes, author is represented by a dict with key
                            # '@orcid' and '#text'
                            if isinstance(entry[key], str):
                                entry[key] = [entry[key]]

                            entry["authors"] = [
                                author["#text"] if isinstance(author, dict) else author \
                                for author in entry[key]
                            ]
                        else:
                            Log.warning("No author found for this DBLP publication:\n%s" % \
                                pformat(entry)
                            )
                        return entry

                    entries = [xml_to_entry(d) for d in result["dblpperson"]["r"]]
                else:
                    raise RuntimeError("Format not implemented: %s" % self.format)
            else:
                raise RuntimeError("Cannot get reply from %s" % self.api_url)

        return self.answer(query, self.reshape_entries(query, entries))
