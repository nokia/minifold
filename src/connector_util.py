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

from .connector import Connector
from .html      import html
from .query     import Query
from .sort_by   import SortByConnector
from .unique    import UniqueConnector

def get_values(connector :Connector, attribute :str):
    enriched_connector = UniqueConnector(
            [attribute],
            connector
        )
    q = Query(attributes = [attribute])
    return [entry[attribute] for entry in enriched_connector.query(q)]

def show_some_values(connector :Connector, limit :int = 5, max_strlen :int = None, query :Query = None):
    if not query:
        query = Query()

    map_values = {
        attribute : get_values(connector, attribute) \
        for attribute in connector.attributes(query.object)
    }

    html(
        """
        <table>
            <tr>
                <th>Attribute</th>
                <th>#values</th>
                <th>%(limit)d first values</th>
            </tr>
            %(rows)s
        </table>
        """ % {
            "limit" : limit,
            "rows"  : "".join(["""
                <tr>
                    <td><code>%(attribute)s</code></td>
                    <td>%(num_values)d</td>
                    <td style="text-align:left"><code>%(values)s</code></td>
                </tr>
                """ % {
                    "attribute"  : attribute,
                    "num_values" : len(map_values[attribute]),
                    "values" : "<br/>".join([
                        str(x)[:max_strlen] for x in map_values[attribute][:limit]
                    ]),
                } for attribute in connector.attributes(query.object)
            ]),
        }
    )
