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

import operator, re
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

    ret = dict()
    soup = BeautifulSoup(s_html, features = "lxml")

    # Extract url_title
    div = soup.find(name="div", attrs={"class" : "gs_or_ggsm"})
    if div:
        a = div.find(name="a")
        if a:
            ret["url_pdf"] = a["href"]

    # Extract url_title, title
    h3 = soup.find(name="h3", attrs={"class" : "gs_rt"})
    if h3:
        a = h3.find(name="a")
        if a:
            ret["url_title"] = a["href"]
            ret["title"] = clean_string(a.text)

    # Extract authors, year, editor
    div = soup.find(name="div", attrs={"class" : "gs_a"})
    if div:
        s = div.text.replace("\xa0", " ")
        Log.debug("s = %s" % s)
        Log.debug(s.split(" - "))
        (authors, conference_year, editor) = s.split(" - ")
        ret["authors"] = [clean_string(a) for a in authors.split(",")]
        Log.debug("conference_year = %r" % conference_year)
        conference_year = [clean_string(elt) for elt in conference_year.split(",")]
        ret["conference"] = conference_year[0] if len(conference_year) == 2 else None
        ret["year"] = int(conference_year[-1])
        ret["editor"] = clean_string(editor)

    # Extract exceprt
    div = soup.find(name="div", attrs={"class" : "gs_rs"})
    if div:
        ret["excerpt"] = clean_string(div.text.strip())

    # Extract num_citations and num_versions
    divs = soup.findAll(name="div", attrs={"class" : "gs_fl"})
    if divs and len(divs) > 1:
        links = divs[1].findAll("a")
        if links:
            if len(links) > 2:
                ret["num_citations"] = extract_first_int(links[2].text)
                ret["url_citations"] = ScholarConf.SCHOLAR_SITE + links[2]["href"]
                ret["cluster_id"]    = extract_first_int(links[2]["href"])
            if len(links) > 4:
                ret["num_versions"] = extract_first_int(links[4].text)
                ret["url_versions"] = ScholarConf.SCHOLAR_SITE + links[4]["href"]
    return ret

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
        #s_html = self._get_http_response(url)

        # <<<<<<< DEBUG
        filename = "/tmp/google_scholar_dump.html"
        import os
        if not os.path.exists(filename):
            response = download(url)
            if isinstance(response, Exception):
                raise response
            s_html = response.text

            with open(filename, "w") as f:
                Log.info("[>>] Writting %s" % filename)
                print(s_html, file=f)
            Log.debug("s_html = %s" % s_html)
        else:
            Log.info("[<<] Reading %s" % filename)
            # For debugging purpose, because you can get filtered if you query Google Scholar too much :(
            with open(filename) as f:
                s_html = "".join(f.readlines())
        # >>>>>>>>>> DEBUG

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
        if object == "publication":
            #article = ScholarArticle()
            #return set(article.keys())
            return {
                "cluster_id",    #: int,
                "conference",    #: str,
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
        if isinstance(self.querier, MinifoldScholarQuerier):
            ret = self.querier.articles
        else:
            ret = [{k : v[0] for (k, v) in article.attrs.items()} for article in self.querier.articles]
        return self.answer(query, ret)
