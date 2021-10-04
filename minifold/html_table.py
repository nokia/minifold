#!/usr/bin/env python3
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from html.parser                    import HTMLParser
from html.entities                  import name2codepoint

from minifold.entries_connector     import EntriesConnector

class HtmlTableParser(HTMLParser):
    def __init__(self, columns :list, output_list :list, keep_entry = None):
        """
        Constructor.
        Args:
            columns: list of string mapping the attribute name
                corresponding with the index. If data is fetch
                for columns having a greater index than
                len(columns), columns[-1] is used, and this
                key may store a list of string values instead
                of a single string. This allow to store data
                stored among several columns in a single attribute.
            output_list: reference to an output list where the
                data will be outputed (one dict per row, one
                key/value per column).
            keep_entry: callback which determine whether an
                must entry must be kept or discard. Pass None
                to filter nothing. This is the opportunity to
                discard a header or irrelevant row.
        """
        HTMLParser.__init__(self)
        self.fetch_data = False
        self.columns    = columns
        self.index      = 0
        self.entries    = output_list
        self.entry      = dict()
        self.value      = str()
        self.keep_entry = keep_entry

    def attributes(self, object :str) -> set:
        return set(self.columns)

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            # Enable fetch data
            self.fetch_data = True

    def handle_endtag(self, tag):
        if tag == "td": # Push key/value
            # Disable fetch data
            self.fetch_data = False

            # Push new key/value pair
            key = self.columns[self.index] if self.index < len(self.columns) else self.columns[-1]
            if key in self.entry.keys():
                current_value = self.entry[key]
                if not isinstance(current_value, list):
                    self.entry[key] = [current_value]
                if self.value:
                    self.entry[key].append(self.value)
            else:
                if self.value:
                    self.entry[key] = self.value

            # Reset key/value pair
            self.value = str()
            self.index += 1
        elif tag == "tr":
            # Push entry
            if self.keep_entry == None or self.keep_entry(self.entry):
                self.entries.append(self.entry)

            # Reset entry
            self.index = 0
            self.entry = dict()

    def handle_data(self, data):
        data = data.strip()
        if self.fetch_data == True and data:
            self.value += data

def html_table(filename :str, columns :list, keep_entry = None) -> list:
    entries = list()
    parser = HtmlTableParser(columns, self.m_entries, keep_entry)
    with open(filename, "r") as f:
        s = f.read()
        parser.feed(s)
    return entries

class HtmlTableConnector(EntriesConnector):
    def __init__(self, filename :str, columns :list, keep_entry = None):
        """
        Constructor.
        Args:
            filename: Input HTML filename.
            columns: list of string mapping the attribute name
                corresponding with the index. If data is fetch
                for columns having a greater index than
                len(columns), columns[-1] is used, and this
                key may store a list of string values instead
                of a single string. This allow to store data
                stored among several columns in a single attribute.
            output_list: reference to an output list where the
                data will be outputed (one dict per row, one
                key/value per column).
            keep_entry: callback which determine whether an
                must entry must be kept or discard. Pass None
                to filter nothing. This is the opportunity to
                discard a header or irrelevant row.
        """
        self.m_entries = list()
        self.m_parser = HtmlTableParser(columns, self.m_entries, keep_entry)
        with open(filename, "r") as f:
            s = f.read()
            self.m_parser.feed(s)
        super().__init__(self.m_entries)


