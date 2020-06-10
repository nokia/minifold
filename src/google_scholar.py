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

try:
    from bs4 import BeautifulSoup
except ImportError as e:
    print(
        "\n  ".join([
            "Please install bs4",
            "APT: sudo apt install python3-bs4",
            "PIP: sudo pip3 install bs4",
        ]),
        file = sys.stderr
    )
    raise e

import difflib, operator, re
from pprint             import pformat, pprint
from .binary_predicate  import BinaryPredicate
from .connector         import Connector
from .download          import download
from .log               import Log
from .query             import ACTION_READ, Query
from .scholar           import ScholarArticle, ScholarConf, ScholarQuerier, ScholarSettings, SearchScholarQuery, SoupKitchen

def parse_article(s_html :str) -> dict:
    """
    Parse a "gs_res_ccl_mid" div (wrapping each article) returned by Google Scholar.
    Args:
        s_html: The HTML string containing the div.
    Returns:
        The dict describing the article, structured as follows:
        {
            "authors"       : list, # The list only contains the first authors. The last author name maybe incomplete.
            "cluster_id"    : int,
            "conference"    : str,  # May be incomplete
            "editor"        : str,
            "excerpt"       : str,  # May be incomplete.
            "num_citations" : int,
            "num_versions"  : int,
            "title"         : str,
            "url_citations" : str,
            "url_versions"  : str,
            "url_pdf"       : str,
            "url_title"     : str,
            "year"          : int,
        }
        An incomplete string may start by '…' and ends with '…'.
        URLs are absolute.
    """
    def clean_string(s :str) -> str:
        return re.sub("( |\xa0|\n)+", " ", s).strip()

    def extract_first_int(s :str) -> int:
        return int(re.search("\d+", s).group())

    entry = dict()
    soup = BeautifulSoup(s_html, features = "lxml")

    # Extract url_title
    div = soup.find(name="div", attrs={"class" : "gs_or_ggsm"})
    if div:
        a = div.find(name="a")
        if a:
            entry["url_pdf"] = a["href"]

    # Extract url_title, title
    h3 = soup.find(name="h3", attrs={"class" : "gs_rt"})
    if h3:
        span = h3.find(name="span", attrs={"class" : "gt_ct1"})
        if span: # [CITATION]
            entry["doc_type"] = span.text[1:-1]
        a = h3.find(name="a")
        if a:
            entry["url_title"] = a["href"]
            entry["title"] = clean_string(a.text)

    # Extract authors, year, editor
    div = soup.find(name="div", attrs={"class" : "gs_a"})
    if div:
        s = div.text.replace("\xa0", " ")
        (authors, conference_year, editor) = s.split(" - ")
        entry["authors"] = [clean_string(a) for a in authors.split(",")]
        conference_year = [clean_string(elt) for elt in conference_year.split(",")]
        entry["conference"] = conference_year[0] if len(conference_year) == 2 else None
        entry["year"] = int(conference_year[-1])
        entry["editor"] = clean_string(editor)

    # Extract exceprt
    div = soup.find(name="div", attrs={"class" : "gs_rs"})
    if div:
        entry["excerpt"] = clean_string(div.text.strip())

    # Extract num_citations and num_versions
    divs = soup.findAll(name="div", attrs={"class" : "gs_fl"})
    if divs and len(divs) > 1:
        links = divs[1].findAll("a")
        if links:
            # It is important to not use link index here as it may change depending on the
            # document (e.g whether it is cited or not).
            for link in links:
                s =  link.text.lower()
                key = "citations" if "cited by" in s else \
                      "versions"  if "versions" in s else \
                      None
                if key:
                    entry["num_%s" % key] = extract_first_int(s)
                    entry["url_%s" % key] = ScholarConf.SCHOLAR_SITE + link["href"]
                    entry["cluster_id"]    = extract_first_int(link["href"])
    return entry

class MinifoldScholarQuerier(ScholarQuerier):
    """
    ScholarQuerier is overloaded to fetch more attributes.
    """
    def __init__(self):
        super().__init__()
        self.articles = list()

    def parse(self, s_html :str):
        soup = SoupKitchen.make_soup(s_html)
        soup = soup.find(name="div", attrs={"id" : "gs_res_ccl_mid"})
        for div in soup.findAll(name="div", attrs={"class" : "gs_r"}):
            s = div.prettify()
            entry = parse_article(s)
            self.articles.append(entry)

    def send_query(self, gs_query):
        # Network
        url = gs_query.get_url()
        Log.info("GoogleScholar <-- %s" % url)

        # Here, we rely on minifold downloader as it can cache results.
        #s_html = self._get_http_response(url)
        response = download(url)
        s_html = response.text

        # Parsing
        assert s_html
        self.parse(s_html)
        self.articles = list()
        self.parse(s_html)

class GoogleScholarConnector(Connector):
    def __init__(self, citation_format :str = ScholarSettings.CITFORM_BIBTEX):
        settings = ScholarSettings()
        settings.set_citation_format(citation_format)
        self.querier = MinifoldScholarQuerier() # ScholarQuerier()
        self.querier.apply_settings(settings)

    def attributes(self, object :str) -> set:
        if object == "publication" or not object:
            #article = ScholarArticle()
            #return set(article.keys())
            return {
                "authors",       #: str
                "cluster_id",    #: int,
                "conference",    #: str,
                "doc_type",      #: str,
                "editor",        #: str,
                "excerpt",       #: str,
                "num_citations", #: int,
                "num_versions",  #: int,
                "title",         #: str,
                "url_citations", #: str,
                "url_versions",  #: str,
                "url_pdf",       #: str,
                "url_title",     #: str,
                "year",          #: int,
            }
        elif object == "cluster":
            raise RuntimeError("Object %s is not yet supported" % object)
        else:
            raise RuntimeError("Invalid object %s" % object)

    @staticmethod
    def filter_to_scholar(p :BinaryPredicate, gs_query :SearchScholarQuery, authors :list):
        if p.operator == operator.__and__:
            GoogleScholarConnector.filter_to_scholar(p.left, gs_query, authors)
            GoogleScholarConnector.filter_to_scholar(p.right, gs_query, authors)
            return

        if isinstance(p.left,  BinaryPredicate) \
        or isinstance(p.right, BinaryPredicate):
            raise RuntimeError("Invalid clause %s" % p)

        attr = p.left
        value = p.right
        if not isinstance(attr, str):
            raise RuntimeError("Invalid left operand %s" % p)

        if attr == "authors":
            if p.operator in {operator.__eq__, operator.__contains__}:
                authors.append(value)
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
            if start is not None and end is not None and end < start:
                raise RuntimeError("Invalid range of date")
            gs_query.set_timeframe(start, end)
        elif attr == "publication":
            if p.operator == operator.__eq__:
                gs_query.set_pub(value)
            else:
                raise RuntimeError("Invalid operator %s" % p)

    @staticmethod
    def sanitize_author(authors :list, author :str) -> str:
        """
        Find in an input list of strings the closest string with the input string.
        Args:
            authors: The list of strings.
            author: The reference string.
        Returns:
            The string of `authors` closest to `author` if any, else `author`
        """
        # Find the best match in authors. Indeed if we search "John Doe", Google Scholar
        # returns "J Doe" and so the self.reshape_entries will drop the records.
        # In practice, the cutoff must be quite low, but not too low. Otherwise,
        # co-authors may be wrongly renamed! Empirically, 0.4 is a good tradeoff).
        l = difflib.get_close_matches(author, authors, n=1, cutoff=0.4)
        if len(l) != 1:
            # We are trying to rename a co-author without knowing is real name.
            return author
        else:
            # We are renaming an author with his/her real name.
            return l[0]

    def query(self, query :Query) -> list:
        super().query(query)
        entries = None
        if query.action != ACTION_READ:
            raise RuntimeError("Action not supported" % query.action)
        if query.filters and not isinstance(query.filters, BinaryPredicate):
            raise RuntimeError("Invalid filter: %s" % query.filters)

        authors = list()
        if query.object == "cluster":
            gs_query = ClusterScholarQuery(cluster=options.cluster_id)
        elif query.object == "publication" or not query.object:
            gs_query = SearchScholarQuery()
            GoogleScholarConnector.filter_to_scholar(query.filters, gs_query, authors)
        else:
            raise RuntimeError("Invalid object %r" % query.object)

        # Craft the query
        if query.limit is not None:
            gs_query.set_num_page_results(min(query.limit, ScholarConf.MAX_PAGE_RESULTS))

        # Doc type.
        gs_query.set_include_citations(False)
        gs_query.set_include_patents(True)

        # Send the query
        self.querier.send_query(gs_query)

        # Extract results
        if isinstance(self.querier, MinifoldScholarQuerier):
            entries = self.querier.articles
        else:
            entries = [
                {k : v[0] for (k, v) in article.attrs.items()}
                for article in self.querier.articles
            ]

        if gs_query.author:
            # Sanitize author list.
            for entry in entries:
                entry["authors"] = [
                    GoogleScholarConnector.sanitize_author(authors, author)
                    for author in entry["authors"]
                ]
        entries = self.reshape_entries(query, entries)
        return self.answer(query, entries)
