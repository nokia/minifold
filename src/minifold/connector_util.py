#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

"""
This file gathers some useful function to get and display
some entries from an abitrary :py:class:`Connector` instance.
"""

from .connector import Connector
from .html import html
from .query import Query
from .unique import UniqueConnector


def get_values(connector: Connector, attribute: str) -> list:
    """
    Retrieves distinct values mapped with a given attribute stored
    in the entries of a given :py:class:`Connector` instance.

    Args:
        connector (Connector): The queried :py:class:`Connector` instance.
        attribute (str): The queried attribute.

    Raises:
        KeyError: if ``attribute`` is not a valid attribute.

    Returns:
        The corresponding values.
    """
    enriched_connector = UniqueConnector(
        [attribute],
        connector
    )
    q = Query(attributes=[attribute])
    return [entry[attribute] for entry in enriched_connector.query(q)]


def show_some_values(
    connector: Connector,
    limit: int = 5,
    max_strlen: int = None,
    query: Query = None
):
    """
    Displays in Jupyter notebook some values for each attribute of the entries
    served by a given :py:class:`Connector` instance.
    This is useful to discover a dataset.

    Args:
        connector (Connector): The queried :py:class:`Connector` instance.
        limit (int): A positive integer or ``None`` (no limit) that upper bounds
            the number of values to be fetched for each attribute.
        query (Query): The :py:class:`Query` instance used to probe ``connector``.
            You may pass ``None`` to issue to default query.
    """
    if not query:
        query = Query()

    map_values = {
        attribute: get_values(connector, attribute)
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
            "limit": limit,
            "rows": "".join(["""
                <tr>
                    <td><code>%(attribute)s</code></td>
                    <td>%(num_values)d</td>
                    <td style="text-align:left"><code>%(values)s</code></td>
                </tr>
                """ % {
                    "attribute": attribute,
                    "num_values": len(map_values[attribute]),
                    "values": "<br/>".join([
                        str(x)[:max_strlen] for x in map_values[attribute][:limit]
                    ]),
                } for attribute in connector.attributes(query.object)
            ]),
        }
    )
