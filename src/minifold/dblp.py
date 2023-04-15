#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

"""
The DBLP Computer science bibliography provides open bibliographic information
on major computer science journals and proceedings.

- `DBLP website <https://dblp.org/>`__
- `API specs <https://wiki.inria.fr/lincs/Dblp-api>`__

Some query examples:

- `Retrieves articles authored by Fabien Mathieu, in JSON format <https://dblp.dagstuhl.de/search/publ/api?q=fabien-mathieu&h=500&format=json>`
- `Retrieves articles authored by Fabien Mathieu pubished in 2014, in JSON format <https://dblp.dagstuhl.de/search/publ/api?q=fabien-mathieu%20year:2014&h=500&format=json>`

By default DBLP only returns up to 30 records (see
`this link <https://dblp.org/faq/How+to+use+the+dblp+search+API.html>`__).

The default limit in :py:class:`DblpConnector` is set to ``9999``.

It is possible to query a specific researcher using its DBLP-ID.
The ID can be found by browsing the page related to a researcher.

Example:
- `Query using the DBLP name <https://dblp.uni-trier.de/pers/hd/c/Chen:Chung_Shue>`
- `Query using the DBLP ID <https://dblp.org/pid/30/1446>`
- The DBLP ID can be obtained by clicking on the export bibliography icon.

For the moment, the only result format supported by DBLP is XML
(see `this link <https://dblp.org/pid/30/1446.xml>`__).
"""

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError as e:
    from .log import Log
    Log.warning(
        "\n".join([
            "Please install requests",
            "  APT: sudo apt install python3-urllib3",
            "  PIP: sudo pip3 install --upgrade urllib3",
        ])
    )
    raise e

try:
    import requests
except ImportError as e:
    from .log import Log
    Log.warning(
        "\n".join([
            "Please install requests",
            "  APT: sudo apt install python3-requests",
            "  PIP: sudo pip3 install --upgrade requests",
        ])
    )
    raise e

try:
    import xmltodict
except ImportError as e:
    from .log import Log
    Log.warning(
        "\n".join([
            "Please install requests",
            "  APT: sudo apt install python3-xmltodict",
            "  PIP: sudo pip3 install --upgrade xmltodict",
        ])
    )
    raise e

import json
import operator
from pprint import pformat

from .binary_predicate import BinaryPredicate
from .connector import Connector
from .doc_type import DocType
from .log import Log
from .strings import to_international_string, to_canonic_fullname as _to_canonic_fullname
from .query import Query, ACTION_READ

# Default queried DBLP API.
DBLP_API_URL = "https://dblp.dagstuhl.de"

# Maps DBLP ontology to our ontology.
DBLP_ALIASES = {
    "type"    : "dblp_doc_type",
    "venue"   : "conference",
    "url"     : "dblp_url",
}

def to_canonic_fullname(s: str) -> str:
    """
    Canonizes an author full name.

    Args:
        s (str): The input fullname.

    Returns:
        The canonizes fullname.
    """
    # DBLP may now returns {"@pid" : int, "text" : "Firstname Lastname"}
    # instead of the author fullname.
    if isinstance(s, dict):
        s = s["text"]
    return _to_canonic_fullname(s)

class DblpConnector(Connector):
    """
    The :py:class:`DblpConnector` class is a minifold gateway allowing to
    fetch data from DBLP (repository of scientific articles).

    See also:
    - :py:class:`HalConnector`.
    - :py:class:`GoogleScholarConnector`.
    """
    def __init__(
        self,
        map_dblp_id: dict = None,
        map_dblp_name: dict = None,
        dblp_api_url: str = DBLP_API_URL
    ):
        """
        Constructor.

        Args:
            map_dblp_id (dict): Maps an author full name with his/her DBLP ID.
            map_dblp_name (dict): Maps an author obsolete full name with his/her
                current full name.
            dblp_api_url (str): The URL of the DBLP server.
                Defaults to :py:data:`DBLP_API_URL`.
        """
        super().__init__()
        self.m_api_url = dblp_api_url
        assert (
            not dblp_api_url.endswith("/search") and
            not dblp_api_url.endswith("/search/")
        ), f"Invalid API URL [{dblp_api_url}], remove '/search/' suffix"
        self.m_format  = "json"  # valid values are in {"xml", "json", "jsonp"}.
        self.m_map_dblp_id = map_dblp_id if map_dblp_id else dict()
        self.m_map_dblp_name = map_dblp_name if map_dblp_name else dict()
        self.m_map_rev_name = {
            to_canonic_fullname(dblp_name) : name
            for (name, dblp_name) in self.m_map_dblp_name.items()
        }

    def attributes(self, object: str) -> set:
        """
        Lists the attributes of the collection of objects stored
        in this :py:class:`DblpConnector` instance.

        Args:
            object (str): The name of the minifold object.
                As a :py:class:`DblpConnector` instance stores a single
                collection, ``object`` is no relevant and you may pass ``None``.

        Returns:
            The set of available ``object``'s attributes
        """

        return {
            "authors", "doc_type", "title", "type", "venue", "url", "year"
        }  # Non exhaustive

    @property
    def api_url(self) -> str:
        """
        Retrieves the URL of the remote DBLP server. managed by
        this :py:class:`DblpConnector` instance.

        Returns:
            The URL of the remote DBLP server.
        """
        return self.m_api_url

    @property
    def format(self) -> str:
        """
        Retrieves the format of data retrieved from the DBLP server.

        Returns:
            A value in ``{"xml", "json", "jsonp"}``.
        """
        return self.m_format

    @property
    def map_dblp_name(self) -> dict:
        """
        Retrieves the dictionary that maps an author obsolete full name with his/her
        current full name.

        Returns:
            The queried dictionary.
        """
        return self.m_map_dblp_name

    @property
    def map_dblp_id(self) -> dict:
        """
        Retrieves the dictionary that maps an author full name with his/her DBLP ID.

        Returns:
            The queried dictionary.
        """
        return self.m_map_dblp_id

    @staticmethod
    def to_dblp_name(s: str, map_dblp_name: dict = None) -> str:
        """
        Converts a fullname to the corresponding current DBLP name.

        Args:
            s (str): The input fullname.

        Returns:
            The (possibly updated) fullname.
        """
        if map_dblp_name:
            s = map_dblp_name.get(s, s)
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

    def get_dblp_name(self, s: str) -> str:
        """
        Retrieves the current DBLP fullname of an author.

        Args:
            s (str): The input fullname.

        Returns:
            The (possibly updated) fullname.
        """
        return DblpConnector.to_dblp_name(s, self.map_dblp_name)

    def get_dblp_id(self, s: str) -> str:
        """
        Retrieves the current DBLP ID of an author.

        Args:
            s (str): The input fullname.

        Returns:
            The corresponding DBLP ID or ``s``.
        """
        pid = self.m_map_dblp_id.get(s)
        return pid if pid else self.get_dblp_name(s)

    def binary_predicate_to_dblp(self, p :BinaryPredicate, result :dict):
        """
        Converts a minifold predicate to a DBLP predicate.

        Args:
            p (BinaryPredicate): A :py:class:`BinaryPredicate` instance.
            result (dict): The output dictionary.
        """
        # Recursive call only supported for && clauses
        if p.operator == operator.__and__:
            self.binary_predicate_to_dblp(p.left, result),
            self.binary_predicate_to_dblp(p.right, result)
            return

        # Simple predicate. The left member must be a attribute name of the entry.
        if not isinstance(p.left, str):
            raise RuntimeError(
                f"binary_predicate_to_dblp: the left operand of {p} must be a string"
            )

        if p.left in ["author", "authors", "researcher", "conference"]:
            # String attribute. Only "CONTAINS" and "==" are supported.
            # "==" behaves like "CONTAINS"
            if p.operator == operator.__eq__ or p.operator == operator.__contains__:
                result["prefix"] = self.get_dblp_name(p.right)
            else:
                raise RuntimeError(
                    f"binary_predicate_to_dblp: unsupported operator ({p.operator}): {p}"
                )
        else:
            # Other attributes. Only "==" is supported.
            if p.operator == operator.__eq__:
                result["suffix"] += "%20" + ("%s:%s" % (p.left, p.right))
            else:
                raise RuntimeError(
                    f"binary_predicate_to_dblp: unsupported operator ({p.operator}): {p}"
                )

    @staticmethod
    def to_doc_type(s: str) -> DocType:
        """
        Converts a DBLP doc type to the corresponding :py:class:`DocType` instance.

        Args:
            s (str): The DBLP doc type.

        Returns:
            The corresponding :py:class:`DocType` instance.
        """
        s = s.lower()
        if s in {
            "article", "conference and workshop papers", "conference or workshop",
            "incollection", "inproceedings", "proceedings"
        }:
            return DocType.ARTICLE
        # elif s == "????":
        #     return DocType.COMM
        elif s == "journal articles":
            return DocType.JOURNAL
        elif s in {"informal publications", "reference works"}:
            return DocType.REPORT
        elif s in {"phdthesis", "books and theses", "parts in books or collections"}:
            return DocType.BOOKS_AND_THESES
        # elif s == "????":
        #     return DocType.HDR
        elif s == "editorship":
            return DocType.CHAPTER
        else:
            Log.warning("DblpConnector.to_doc_type: unknown type: %s" % s)
            return DocType.UNKNOWN

    def reshape_entry(self, query: Query, entry: dict) -> dict:
        """
        Reshape a DBLP entry to make it compliant with a given
        :py:class:`Query` instance.

        Args:
            query (Query): A :py:class:`Query` instance.
            entry (dict): The entry to reshape.

        Returns:
            The reshaped entry.
        """
        if "type" in entry.keys():
            doc_type = DblpConnector.to_doc_type(entry["type"])
            entry["doc_type"]      = doc_type  # Compatible with Hal "doc_type" values.
            entry["dblp_doc_type"] = doc_type  # To compare Hal and DBLP doc_types.

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
                self.m_map_rev_name.get(_to_canonic_fullname(author), author)
                for author in entry["authors"]
            ]

        return entry

    def extract_entries(self, query: Query, results: list) -> list:
        """
        Extracts the minifold entries for a DBLP query result.

        Args:
            query (Query): A :py:class:`Query` instance.
            results: The DBLP results.

        Returns:
            A ``list`` of ``dict`` instances (the minifold entres).
        """
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
                        # Log.warning("Ignoring %(title)s %(authors)s (homonym)" % entry)
                        continue

                entries.append(entry)
        except KeyError:  # Occurs if 0 DBLP publication found
            pass
        return entries

    def reshape_entries(self, query: Query, entries: list) -> list:
        """
        Apply :py:meth:`DblpConnector.reshape_entry` to a list of entries.

        Args:
            query (Query): A :py:class:`Query` instance.
            entries (list): A list of minifold entries.

        Returns:
            The reshaped entries.
        """
        return [self.reshape_entry(query, entry) for entry in entries]

    def query(self, query: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching ``query``.
        """
        super().query(query)
        entries = list()
        if query.action == ACTION_READ:

            pid = None
            format = self.format
            object = ""
            url_options = list()
            if query.object == "publication":
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
                if pid:
                    format = "xml"
                else:
                    url_options.append(dblp_name)

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
            reply = requests.get(q_dblp, timeout=(5, 5))

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

                    def xml_to_entry(d: dict) -> dict:
                        """
                        Converts a dictionary obtained from XML result returned
                        by DBLP to a flat dictionary.

                        Args:
                            d: The DBLP dictionary.

                        Returns:
                            The corresponding flat dictionary.
                        """
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
                                author["#text"] if isinstance(author, dict) else author
                                for author in entry[key]
                            ]
                        else:
                            Log.warning(f"No author found for this DBLP publication:\n{pformat(entry)}")
                        return entry

                    entries = [xml_to_entry(d) for d in result["dblpperson"]["r"]]
                else:
                    raise RuntimeError("Format not implemented: %s" % self.format)
            else:
                raise RuntimeError("Cannot get reply from %s" % self.api_url)

        return self.answer(query, self.reshape_entries(query, entries))
