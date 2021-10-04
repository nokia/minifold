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

import re, sys
from html       import escape
from .connector import Connector
from .query     import Query

PATTERN_URL = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

#def str_to_html(s :str) -> str:
#    if PATTERN_URL.match(s):
#        return "<a href=%s>%s</a>" % (s, s)
#    else:
#        return s.rstrip(".").rstrip(",")

def str_to_html(s :str) -> str:
    #return escape(s).rstrip(".").rstrip(",")
    return s.rstrip(".").rstrip(",")

def to_html_link(d :dict, k :str, v :str) -> str:
    try:
        return "<a href=\"%s\">%s</a>" % (d[k], escape(v))
    except KeyError:
        return v

def value_to_html(x) -> str:
    if isinstance(x, dict):
        ret = dict_to_html(x, x.keys())
    elif isinstance(x, str):
        if PATTERN_URL.match(x):
            ret = "<a href=\"%s\">%s</a>" % (x, escape(x))
        else:
            ret = str_to_html(x)
    elif isinstance(x, (list, set)):
        ret = ", ".join([value_to_html(value) for value in x])
    else:
        ret = escape("%s" % x)
    return ret

def html(s :str):
    """
    Evaluate HTML code in a Jupyter Notebook.
    Args:
        s: A str containing HTML code.
    """
    from IPython.display import display, HTML
    chart = HTML(s)
    # or chart = charts.plot(...)
    display(chart)

def print_error(x):
    """
    Print an error in a Jupyter Notebook.
    """
    print(str(x), file = sys.stderr)

def entries_to_html(entries :list, map_attribute_label :dict = dict(), attributes :list = None) -> str:
    """
    Export to HTML a list of dict.
    Args:
        entries: A list of dicts
        map_attribute_label: A dict {str : str} which maps each entry key with the column header
            to display.
        attributes: The subset of keys to display.
    """

def entries_to_html(
    entries :list,
    map_attribute_label :dict = None,
    attributes :list = None,
    keep_entry_if :callable = None
) -> str:
    if not attributes:
        attributes = list(entries[0].keys())
    if not keep_entry_if:
        keep_entry_if = lambda i, entry: True
    if not map_attribute_label:
        map_attribute_label = dict()
    return """
        <div style="width:100%%; overflow-x: auto;white-space: nowrap;">
            <table>
                %(header)s
                %(rows)s
            </table>
        </div>
        """ % {
            "header" : "<tr>%s</tr>" % "".join(
                ["<th>Index</th>"] + [
                    "<th style='text-align: left;white-space: nowrap;'>%s</th>" % str(map_attribute_label.get(attribute, attribute))
                    for attribute in attributes
                ]
            ),
            "rows" : "".join([
                """
                <tr>
                    <td>%(index)d</td>
                    %(values)s
                </tr>
                """ % {
                    "index" : i,
                    "values" : "".join([
                        "<td style='text-align: left;white-space: nowrap;'>%s</td>" % value_to_html(entry.get(attribute))
                        for attribute in attributes
                    ])
                }
                for (i, entry) in enumerate(entries)
                if keep_entry_if(i, entries)
            ]),
        }

def connector_to_html(connector :Connector, **kwargs) -> str:
    attributes = kwargs.get("attributes")
    if not attributes:
        attributes = connector.attributes(None)
    entries = connector.query(Query(**kwargs))
    return entries_to_html(entries, attributes=attributes)

def entry_to_html(entry :dict, map_attribute_label :dict = dict(), attributes :list = None) -> str:
    return entries_to_html([entry], map_attribute_label, attributes)

# OBSOLETE
def dict_to_html(d :dict, attributes :list, map_attribute_label :dict = dict()) -> str:
    return entry_to_html(d, map_attribute_label, attributes)

#----------------------------------------------------------------------------------
# Extensions depending on BeautifulSoup
#----------------------------------------------------------------------------------

try:
    # See https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/
    from bs4 import BeautifulSoup

    HTML_BLACKLIST_TAGS = {
        "[document]",
        "noscript",
        "header",
        "html",
        "head",
        "link",
        "input",
        "meta",
        "script",
        "style"
    }

    def html_to_text(s_html :str, blacklist :set = HTML_BLACKLIST_TAGS) -> str:
        """
        Convert an HTML page to text, by discarding javascript and css related
        to the site.
        Args:
            s_html: A str containing HTML.
            blacklist: A set of str (lowercase) corresponding to HTML tags
                that must be ignored.
        """
        soup = BeautifulSoup(s_html, features = "lxml")
        soup.find_all(s_html, "html.parser")
        text = soup.find_all(text = True)
        l = list()
        for t in text:
            s = t.strip()
            if s and t.parent.name not in blacklist:
                #print("<%s>: %r" % (t.parent.name, s))
                s = re.sub("<[^>]*>", "", s)
                l += [s]
        s = " ".join(l)
        return re.sub(r"[\n]+", "\n\n", s)

    HTML_MAP_WHITELIST_ATTRS = {
        "a"   : ["href"],
        "img" : ["src"],
    }

    # Based on https://gist.github.com/revotu/21d52bd20a073546983985ba3bf55deb
    def remove_all_attrs_except_saving(soup, whitelist = HTML_MAP_WHITELIST_ATTRS):
        """
        Remove all attributes except some.
        Args:
            soup: A BeautifulSoup instance, modified in place.
            whitelist: A dict {tag : list(attr)} where tag is an HTML tag and attr
                an HTML attribute.
        """
        for tag in soup.find_all(True):
            if tag.name not in whitelist.keys():
                tag.attrs = {}
            else:
                attrs = dict(tag.attrs)
                allowed_attrs = whitelist[tag.name]
                for attr in attrs:
                    if attr not in allowed_attrs:
                        del tag.attrs[attr]
                    elif attr == "href" and not attr.startswith("http"):
                        tag.attrs[attr] = "#"
        return soup

    def remove_tags(soup, blacklist :set = HTML_BLACKLIST_TAGS):
        """
        Remove some HTML tags.
        Args:
            soup: A BeautifulSoup instance, modified in place.
            blacklist: A list of str, where each str is an HTML tag.
        """
        for tag in blacklist:
            while True:
                attr = getattr(soup, tag)
                if attr:
                    attr.decompose()
                else:
                    break

    def sanitize_html(
        s_html       :str,
        blacklist    :set  = HTML_BLACKLIST_TAGS,
        remove_attrs :bool = True
    ) -> str:
        """
        Remove from an HTML string irrelevants HTML blocks and attributes.

        /!\ This function is SLOW so do not use it on large corpus!

        Args:
            s_html: A str instance containing HTML.
            blacklist: List of blacklisted HTML tags.
        Returns:
            The sanitized string.
        """
        soup = BeautifulSoup(s_html, features = "lxml")
        if remove_attrs:
            remove_all_attrs_except_saving(soup)
        body = soup.find("body")
        if not body:
            return None
        remove_tags(body, blacklist)
        return str(body.prettify())

except ImportError as e:
    #print(
    #    "\n  ".join([
    #        "Please install bs4",
    #        "APT: sudo apt install python3-bs4",
    #        "PIP: sudo pip3 install bs4",
    #    ]),
    #    file = sys.stderr
    #)
    pass

