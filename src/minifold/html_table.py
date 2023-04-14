#!/usr/bin/env python3
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from html.parser            import HTMLParser
from .log                   import Log
from .entries_connector     import EntriesConnector

class HtmlTableParser(HTMLParser):
    def __init__(self, columns: list, output_list: list, keep_entry: callable = None):
        """
        Constructor.

        Args:
            columns (list): A list of string mapping the attribute name
                corresponding with the index. If data is fetch
                for columns having a greater index than
                len(columns), columns[-1] is used, and this
                key may store a list of string values instead
                of a single string. This allow to store data
                stored among several columns in a single attribute.
            output_list (list): A reference to an output list where the
                data will be output (one dict per row, one
                key/value per column).
            keep_entry (callable): A callback which determines whether an
                must entry must be kept or discarded. Pass ``None``
                to filter nothing. This is the opportunity to
                discard a header or irrelevant rows.
        """
        HTMLParser.__init__(self)
        self.fetch_data = False
        self.columns    = columns
        self.index      = 0
        self.entries    = output_list
        self.entry      = dict()
        self.value      = str()
        self.keep_entry = keep_entry

    # Inherited abstract method
    def error(self, message: str):
        """
        Logs an error message.

        Args:
            message (str): The error message.
        """
        Log.error(message)

    def handle_starttag(self, tag: str, attrs: str):
        """
        Callback that handles an opening HTML tag (e.g., ``"<td>"``).

        Args:
            tag (str): The HTML tag. _Example:_ ``"td"``.
            attrs (str): The HTML tag attributes.
        """
        if tag == "td":
            # Enable fetch data
            self.fetch_data = True

    def handle_endtag(self, tag):
        """
        Callback that handles an opening HTML tag (e.g., ``"</td>"``).

        Args:
            tag (str): The HTML tag. _Example:_ ``"td"``.
        """
        if tag == "td":  # Push key/value
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
            if self.keep_entry is None or self.keep_entry(self.entry):
                self.entries.append(self.entry)

            # Reset entry
            self.index = 0
            self.entry = dict()

    def handle_data(self, data: str):
        """
        Callback that handles an opening HTML data.

        Args:
            data (str): The HTML data (here, stored in a table cell).
        """
        data = data.strip()
        if self.fetch_data and data:
            self.value += data

def html_table(filename: str, columns: list, keep_entry: bool = None) -> list:
    """
    Loads an HTML table from an input file

    Args:
        filename (str): The path to the input HTML file.
        columns (list): A list of string mapping the attribute name
            corresponding with the index. If data is fetch
            for columns having a greater index than
            len(columns), columns[-1] is used, and this
            key may store a list of string values instead
            of a single string. This allow to store data
            stored among several columns in a single attribute.
        keep_entry (callable): A callback which determines whether an
            must entry must be kept or discarded. Pass ``None``
            to filter nothing. This is the opportunity to
            discard a header or irrelevant rows.

    Returns:
        The corresponding list of minifold entries.
    """
    entries = list()
    parser = HtmlTableParser(columns, entries, keep_entry)
    with open(filename, "r") as f:
        s = f.read()
        parser.feed(s)
    return entries

class HtmlTableConnector(EntriesConnector):
    """
    The :py:class:`HtmlTableConnector` class is a minifold gateway allowing
    to fetch data stored in an HTML table.
    """
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
            keep_entry: callback which determine whether an
                must entry must be kept or discard. Pass None
                to filter nothing. This is the opportunity to
                discard a header or irrelevant row.
        """
        super().__init__(list())
        self.m_parser = HtmlTableParser(columns, self.m_entries, keep_entry)
        with open(filename, "r") as f:
            s = f.read()
            self.m_parser.feed(s)
        super().__init__(self.m_entries)

    def attributes(self, object: str = None) -> set:
        """
        Lists available attributes related to a given collection of
        minifold entries exposed by this :py:class:`Connector` instance.

        Args:
            object (str): The name of the collection.
                As this connector stores a single collection, you may pass ``None``.
                Defaults to ``None``.

        Returns:
            The set of corresponding attributes.
        """
        return set(self.m_parser.columns)
