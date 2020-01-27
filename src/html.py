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

try:
    # See https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/
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

