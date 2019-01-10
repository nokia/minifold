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

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    raise ImportError("HalConnector requires python3-urllib3: please run: apt-get install python3-urllib3")

import json, urllib.parse

from .binary_predicate      import BinaryPredicate
from .connector             import Connector
from .doc_type              import DocType
from .log                   import Log
from .strings               import to_international_string, to_canonic_fullname
from .query                 import Query, ACTION_READ, SORT_ASC

# Default HAL API queried
HAL_API_URL = "https://api.archives-ouvertes.fr/search"

# Maps HAL ontology to our ontology
# Note: this is not an exhaustive list of the attributes returned by HAL.
HAL_ALIASES = {
    "en_abstract_s"         : "abstract",
    "fr_abstract_s"         : "abstract_fr",
    "authFullName_s"        : "authors",
    "bookTitle_s"           : "book",
    "citationFull_s"        : "citation_full",
    "city_s"                : "city",
    "conferenceTitle_s"     : "conference",
    "conferenceEndDateD_i"  : "conference_day",
    "conferenceEndDateM_i"  : "conference_month",
    "conferenceEndDateY_i"  : "conference_year",
    "conferenceEndDate_s"   : "conference_date",
    "conferenceOrganizer_s" : "conference_organizer",
    "country_s"             : "country_code",
    "docType_s"             : "hal_doc_type",
    "en_title_s"            : "en_title",
    "fr_title_s"            : "fr_title",
    "fileMain_s"            : "url_viewer",
    "files_s"               : "pdf",
    "journalTitle_s"        : "journal",
    "modifiedDateD_i"       : "date_modified_day",
    "modifiedDateM_i"       : "date_modified_month",
    "modifiedDateY_i"       : "date_modified_year",
    "modifiedDate_s"        : "date_modified",
    "keyword_s"             : "keywords",
    "title_s"               : "title",
    "producedDateD_i"       : "day",
    "producedDateM_i"       : "month",
    "producedDateY_i"       : "year",
    "producedDate_s"        : "date_produced",
    "releasedDateD_i"       : "date_released_day",
    "releasedDateM_i"       : "date_released_month",
    "releasedDateY_i"       : "date_released_year",
    "releasedDate_s"        : "date_released",
    "structId_i"            : "laboratory",
    "submittedDateD_i"      : "date_submitted_day",
    "submittedDateM_i"      : "date_submitted_month",
    "submittedDateY_i"      : "date_submitted_year",
    "submittedDate_s"       : "date_submitted",
    "uri_s"                 : "hal_url",
    "version_i"             : "version"
}

class HalConnector(Connector):
    def __init__(self, map_hal_id = {}, map_hal_name = {}, hal_api_url = HAL_API_URL):
        super().__init__()
        self.m_api_url      = hal_api_url
        self.m_format       = "json"
        self.m_map_hal_id   = map_hal_id
        self.m_map_hal_name = map_hal_name
        self.m_map_rev_name = {to_canonic_fullname(hal_name) : name for (name, hal_name) in map_hal_name.items()}

    @property
    def api_url(self) -> str:
        return self.m_api_url

    @property
    def format(self) -> str:
        return self.m_format

    @property
    def map_hal_id(self) -> dict:
        return self.m_map_hal_id

    @property
    def map_hal_name(self) -> dict:
        return self.m_map_hal_name

    @staticmethod
    def quote(s) -> str:
        return "%%22%s%%22" % s

    @staticmethod
    def to_hal_name(s, map_name = {}) -> str:
        ret = map_name.get(s)
        if ret is None:
            s = s.lower()
            s = s.replace(" ", "-")
            s = s.replace("ç", "%C3%A7") # Merci aux François
            ret = to_international_string(s)
        return ret

    @staticmethod
    def string_to_hal(s) -> str:
        #Only non-french accent must be removed
        s = s.replace("š", "s") # Merci Ana :)
        s = s.replace("ć", "c") # La même :)
        s = urllib.parse.quote(s)
        return HalConnector.quote(s)

    @staticmethod
    def binary_predicate_to_hal(p :BinaryPredicate) -> str:
        if p.operator == "&&":
            return "%s&fq=%s" % (
                HalConnector.binary_predicate_to_hal(p.left),
                HalConnector.binary_predicate_to_hal(p.right)
            )
        if isinstance(p.left, BinaryPredicate):
            raise RuntimeError("binary_predicate_to_hal: Invalid left operand in %s: nested clauses not supported" % p)
        if isinstance(p.right, BinaryPredicate):
            raise RuntimeError("binary_predicate_to_hal: Invalid right operand in %s: nested clauses not supported" % p)
        if not isinstance(p.left, str):
            raise RuntimeError("binary_predicate_to_hal: left operand of %s must be a string" % p)

        right = p.right
        if isinstance(right, str):
            right = HalConnector.string_to_hal(right)

        if   p.operator == "==":
            ret = "%s:(%s)" % (p.left, right)
        elif p.operator == "~":
            ret = "%s:\"%s\"~3" % (p.left, right)
        elif p.operator == ">":
            ret =  "%s:{%s TO *]" % (p.left, right)
        elif p.operator == "<":
            return "%s:[* TO %s}" % (p.left, right)
        elif p.operator == ">=":
            ret = "%s:[%s TO *]" % (p.left, right)
        elif p.operator == "<=":
            ret = "%s:[* TO %s]" % (p.left, right)
        elif p.operator == "IN":
            (start, end) = right
            ret = "%s:[%s TO %s]" % (p.left, start, end)
        else:
            raise RuntimeError("binary_predicate_to_hal: unsupported operator (%s): %s" % (p.operator, p))

        # Space in HAL operators must also be replaced
        return ret.replace(" ", "%20")

    @staticmethod
    def sanitize_dict(d :dict) -> dict:
        for k, v in d.items():
            if isinstance(v, list):
                if len(v) == 1:
                    d[k] = v[0]
                elif k == "title_s":
                    d[k] = " ".join(v)
        return d

    @staticmethod
    def to_doc_type(s :str) -> DocType:
        ret = DocType.UNKNOWN

        # TODO: use dict()
        s = s.lower()
        if   s in ["these", "ouv"]:
            ret = DocType.BOOKS_AND_THESES
        elif s in ["comm"]:
            ret = DocType.ARTICLE
        elif s == "douv":
            # "douv" means "direction d'ouvrage" (aka proceedings)
            ret = DocType.ARTICLE
        elif s == "art":
            # Unfortunately, "art" may design journal articles
            ret = DocType.JOURNAL
        elif s in ["lecture", "report", "mem", "presconf"]:
            # "mem" (mémoires) can be used for internship report. presconf = keynote
            ret = DocType.REPORT
        elif s == "poster":
            ret = DocType.POSTER
        elif s == "hdr":
            ret = DocType.HDR
        elif s in "couv":
            ret = DocType.CHAPTER
        elif s == "patent":
            ret = DocType.PATENT
        elif s in ["undefined", "other"]:
            ret = DocType.UNKNOWN
        elif s == None:
            pass
        else:
            raise ValueError("HalConnector: unknown document type %r" %s)

        return ret

    def sanitize_entry(self, entry :dict) -> dict:
        entry = HalConnector.sanitize_dict(entry)
        keys = entry.keys()

        # << WORKAROUND: Otherwise sometimes the title is not returned ?!
        if "title" not in keys:
            for title_key in ["title_en", "title_fr"]:
                try:
                    entry["title"] = entry[title_key]
                    break
                except KeyError:
                    pass
        # >> WORKAROUND

        if "docType_s" in keys:
            try:
                entry["doc_type"] = HalConnector.to_doc_type(entry["docType_s"])
            except ValueError as e:
                Log.warning("Invalid doc_type: %s" % e)
                Log.warning(entry)
                entry["doc_type"] = DocType.UNKNOWN

        if "authFullName_s" in keys:
            if isinstance(entry["authFullName_s"], str):
                entry["authFullName_s"] = [entry["authFullName_s"]]
            elif isinstance(entry["authFullName_s"], list):
                pass
            else:
                Log.warning("Invalid author list: %s", entry["authFullName_s"])

            # Convert HAL names to our names if needed.
            entry["authFullName_s"] = [
                self.m_map_rev_name.get(to_canonic_fullname(author), author) \
                for author in entry["authFullName_s"]
            ]

        return entry

    def sanitize_entries(self, entries :list) -> list:
        return [self.sanitize_entry(entry) for entry in entries]

    def query(self, q :Query) -> list:
        super().query(q)
        entries = list()
        if q.action == ACTION_READ:
            attributes = None
            if len(q.attributes) > 0:
                attributes = ",".join(q.attributes)
                if "doc_type" in q.attributes and "hal_doc_type" not in q.attributes: attributes += ",docType_s"
            else:
                # Note: this avoid to pull by default every fields provided by HAL.
                attributes = "*"

            object = None
            if q.object == "lincs":
                object = "structId_i:(160294)"
            elif q.object == "publication":
                object = "*:*"
            else:
                # This is not a standard HAL object.
                # By convention, we assume that the user is querying
                # publications related to a researcher.
                try:
                    # Try to consider the object as a HAL ID.
                    hal_id = self.map_hal_id[q.object]
                    object = "*:*&fq=authIdHal_s:(%s)" % HalConnector.quote(self.map_hal_id[q.object])
                except KeyError:
                    # If not found, try to translate the string using self.map_hal_name.
                    # Else, use the provided name.
                    hal_name = HalConnector.to_hal_name(q.object, self.map_hal_name)
                    object = "authFullName_t:(%%22%s%%22)" % HalConnector.quote(hal_name.replace(" ", "%%20"))

            if object == None:
                raise RuntimeError("Object not supported: %s" % q.object)

            url_options = [object]
            if attributes   != None:
                url_options.append("fl=%s" % attributes)
            if q.filters    != None:
                url_options.append("fq=%s" % HalConnector.binary_predicate_to_hal(q.filters))
            url_options.append("rows=%s" % (int(q.limit) if q.limit else 2000))
            if q.sort_by    != None:
                url_options.append("sort=%s" % ",".join([
                    "%s+%s" % (
                        attribute,
                        "asc" if sort_asc == SORT_ASC else "desc"
                    ) for attribute, sort_asc in q.sort_by.items()
                ]))

            url_options += ["sort=submittedDate_tdate+desc", "wt=%s" % self.format]

            # Hardcoded rows=2000 to guarantee that all publications are fetched.
            q_hal = "%(server)s/?q=%(options)s" % {
                "server"  : self.api_url,
                "options" : "&".join(url_options)
            }

            Log.info("--> HAL: %s" % q_hal)
            http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=2.0))
            reply = http.request("GET", q_hal)
            if reply.status == 200:
                if self.m_format == "json":
                    data = json.loads(reply.data.decode("utf-8"))
                    try:
                        entries = self.sanitize_entries(
                            data["response"]["docs"]
                        )
                    except KeyError: # if "response" is not found, an error has occurred
                        from pprint import pformat
                        raise RuntimeError("HAL error:\n%s" % pformat(data))
                else:
                    raise RuntimeError("Format not implemented: %s" % self.m_format)
            else:
                raise RuntimeError("Cannot get reply from %s (status %s)" % (
                    self.m_api_url,
                    reply.status
                ))

        return self.answer(q, entries)

