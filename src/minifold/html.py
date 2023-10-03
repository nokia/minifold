#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

"""
This file gathers some utilities to process, render, or make HTML
strings in minifold.
"""

import re
import sys
from html import escape
from .connector import Connector
from .query import Query

# Regular expression matching an URL
PATTERN_URL = re.compile(
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

# def to_html_link(d: dict, k: str, v: str) -> str:
#     try:
#         return "<a href=\"%s\">%s</a>" % (d[k], escape(v))
#     except KeyError:
#         return v


def value_to_html(x: object) -> str:
    """
    Converts a value to its corresponding HTML string.

    Args:
        x (object): The input value.

    Returns:
        The corresponding HTML string.
    """
    def str_to_html(s: str) -> str:
        """
        Right-strips ``"."`` and ``","`` from a string.

        Args:
            s (str): The input string.
        """
        return s.rstrip(".").rstrip(",")

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


def html(s: str):
    """
    Evaluates HTML code in a Jupyter Notebook.

    Args:
        s: A str containing HTML code.
    """
    from IPython.display import display, HTML
    chart = HTML(s)
    # or chart = charts.plot(...)
    display(chart)


def print_error(x: object):
    """
    Prints an error in a Jupyter Notebook.

    Args:
        x: An expection.
    """
    print(str(x), file=sys.stderr)


def entries_to_html(
    entries: list,
    map_attribute_label: dict = None,
    attributes: list = None,
    keep_entry_if: callable = None
) -> str:
    """
    Exports to HTML a list of dict.

    Args:
        entries: A list of dicts
        map_attribute_label: A ``dict{str: str}`` which maps each
            entry key with the column header to display.
        attributes: The subset of keys to display.
        keep_entry_if: Callback allowing to filter some entries

    Returns:
        The corresponding HTML string.
    """
    if not attributes:
        attributes = list(entries[0].keys())
    if keep_entry_if is None:
        def keep_entry_if(i, entry):
            return True
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
            "header": "<tr>%s</tr>" % "".join(
                ["<th>Index</th>"] + [
                    "<th style='text-align: left;white-space: nowrap;'>%s</th>"
                    % str(map_attribute_label.get(attribute, attribute))
                    for attribute in attributes
                ]
            ),
            "rows": "".join([
                """
                <tr>
                    <td>%(index)d</td>
                    %(values)s
                </tr>
                """ % {
                    "index": i,
                    "values": "".join([
                        "<td style='text-align: left;white-space: nowrap;'>%s</td>"
                        % value_to_html(entry.get(attribute))
                        for attribute in attributes
                    ])
                }
                for (i, entry) in enumerate(entries)
                if keep_entry_if(i, entries)
            ]),
        }


def connector_to_html(connector: Connector, **kwargs) -> str:
    attributes = kwargs.get("attributes")
    if not attributes:
        attributes = connector.attributes(None)
    entries = connector.query(Query(**kwargs))
    return entries_to_html(entries, attributes=attributes)


def entry_to_html(
    entry: dict,
    map_attribute_label: dict = None,
    attributes: list = None
) -> str:
    return entries_to_html([entry], map_attribute_label, attributes)


# OBSOLETE
def dict_to_html(
    d: dict,
    attributes: list,
    map_attribute_label: dict = None
) -> str:
    return entry_to_html(d, map_attribute_label, attributes)


# ----------------------------------------------------------------------------------
# Extensions depending on BeautifulSoup
# ----------------------------------------------------------------------------------

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

    def html_to_text(s_html: str, blacklist: set = None) -> str:
        """
        Converts an HTML page to text, by discarding javascript and css related
        to the site.

        Args:
            s_html (str): A str containing HTML.
            blacklist (set): A set of string (lowercase) corresponding to HTML tags
                that must be ignored.

        Returns:
            The corresponding text.
        """
        if blacklist is None:
            blacklist = HTML_BLACKLIST_TAGS
        soup = BeautifulSoup(s_html, features="lxml")
        soup.find_all(s_html, "html.parser")
        text = soup.find_all(string=True)
        values = list()
        for t in text:
            s = t.strip()
            if s and t.parent.name not in blacklist:
                # print("<%s>: %r" % (t.parent.name, s))
                s = re.sub("<[^>]*>", "", s)
                values += [s]
        s = " ".join(values)
        return re.sub(r"[\n]+", "\n\n", s)

    HTML_MAP_WHITELIST_ATTRS = {
        "a": ["href"],
        "img": ["src"],
    }

    # Based on https://gist.github.com/revotu/21d52bd20a073546983985ba3bf55deb
    def remove_all_attrs_except_saving(soup: BeautifulSoup, whitelist: dict = None):
        """
        Removes all attributes except some.

        Args:
            soup (BeautifulSoup): A BeautifulSoup instance, modified in place.
            whitelist: A ``dict{tag: list(attr)}`` where tag is an HTML tag and attr
                an HTML attribute.
        """
        if whitelist is None:
            whitelist = HTML_MAP_WHITELIST_ATTRS
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

    def remove_tags(soup: BeautifulSoup, blacklist: set = None):
        """
        Removes some HTML tags.

        Args:
            soup(BeautifulSoup): A BeautifulSoup instance, modified in place.
            blacklist (set): A list of str, where each str is an HTML tag.
        """
        if blacklist is None:
            blacklist = HTML_BLACKLIST_TAGS
        for tag in blacklist:
            while True:
                attr = getattr(soup, tag)
                if attr:
                    attr.decompose()
                else:
                    break

    def sanitize_html(
        s_html: str,
        blacklist: set = None,
        remove_attrs: bool = True
    ) -> str:
        """
        Removes from an HTML string irrelevant HTML blocks and attributes.
        Warning: This function is SLOW so do not use it on large corpus!

        Args:
            s_html (str): A str instance containing HTML.
            blacklist (set): List of blacklisted HTML tags.
            remove_attrs (bool): Pass ``True`` to remove HTML tag attributes.

        Returns:
            The sanitized string.
        """
        if blacklist is None:
            blacklist = HTML_BLACKLIST_TAGS
        soup = BeautifulSoup(s_html, features="lxml")
        if remove_attrs:
            remove_all_attrs_except_saving(soup)
        body = soup.find("body")
        if not body:
            return None
        remove_tags(body, blacklist)
        return str(body.prettify())

except ImportError as e:
    from .log import Log
    Log.warning(
        "Please install pymongo.\n"
        "  APT: sudo apt install python3-bs4\n"
        "  PIP: sudo pip3 install --upgrade bs4\n"
    )
    raise e
