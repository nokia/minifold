#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from copy import deepcopy

ACTION_CREATE = 0  # For INSERT ... queries
ACTION_READ = 1    # For SELECT ... queries
ACTION_UPDATE = 2  # For UPDATE ... queries
ACTION_DELETE = 3  # For DELETE ... queries

SORT_ASC = True    # For ... SORT BY ... ASC queries
SORT_DESC = False  # For ... SORT BY ... DESC queries

def action_to_str(action: int) -> str:
    """
    Converts an :py:class:`Query` action to its corresponding string.

    Args:
        action (int): A value in
            :py:data:`ACTION_CREATE`,
            :py:data:`ACTION_READ`,
            :py:data:`ACTION_UPDATE`,
            :py:data:`ACTION_DELETE`.

    Returns:
        The corresponding string.
    """
    if action == ACTION_CREATE:
        return "INSERT"
    elif action == ACTION_READ:
        return "SELECT"
    elif action == ACTION_UPDATE:
        return "UPDATE"
    elif action == ACTION_DELETE:
        return "DELETE"
    else:
        raise RuntimeError("action_to_str: invalid action %s" % action)

class Query:
    def __init__(
        self,
        action = ACTION_READ,
        object: str = "",
        attributes: list = None,
        filters: object = None,
        offset: int = None,
        limit: int = None,
        sort_by: dict = None
    ):
        """
        Constructor.

        Args:
            action (int): A value in
                :py:data:`ACTION_CREATE` (in SQL, INSERT queries),
                :py:data:`ACTION_READ` (in SQL, SELECT queries),
                :py:data:`ACTION_UPDATE` (in SQL, UPDATE queries),
                :py:data:`ACTION_DELETE` or ``None`` (in SQL, DELETE queries).
                Passing ``None`` is equivalent to :py:data:`ACTION_CREATE`.
                Defaults to ``None``.
            object (str): The queried object collection (some minifold gateways
                may host several entries collections, identified by a name).
                Defaults to ``""``.
            attributes (list): A list of attributes. In SQL, this corresponds
                to the attributes pass to `SELECT`.
            filters (object): A minifold filter. In SQL, this corresponds
                to the WHERE clause. See also
                the :py:class:`BinaryPredicate`a and the :py:class:`SearchFilter`
                classes.
            offset (int): A positive integer or ``None`` if not needed.
                In SQL this corresponds to the OFFSET statement.
            limit (int): A positive integer or ``None`` if not needed.
                In SQL this corresponds to the LIMIT statement.
            sort_by (dict): A dictionary characterizing how to sort the results.
                It maps each attributes to be sorted with the corresponding
                sorting order (:py:data:`SORT_ASC` or :py:data:`SORT_DESC`).
                In SQL this corresponds to the SORT BY statement.
        """
        self.m_action = action
        self.m_object = object
        self.m_attributes = list(attributes) if attributes else list()
        self.m_filters = filters

        # NOTE/TODO: the following specifiers are not supported by all the connectors
        self.m_offset = offset
        self.m_limit = limit
        self.m_sort_by = sort_by if sort_by else dict()

    def copy(self):
        """
        Copies this :py:class:`Query` instance.

        Returns:
            The copied :py:class:`Query` instance.
        """
        return deepcopy(self)

    @property
    def action(self) -> int:
        return self.m_action

    @action.setter
    def action(self, value: int):
        self.m_action = value

    @property
    def attributes(self) -> list:
        return self.m_attributes

    @attributes.setter
    def attributes(self, value: list):
        self.m_attributes = value

    @property
    def filters(self):
        return self.m_filters

    @filters.setter
    def filters(self, value):
        self.m_filters = value

    @property
    def limit(self) -> int:
        return self.m_limit

    @limit.setter
    def limit(self, value: int):
        self.m_limit = value

    @property
    def offset(self) -> int:
        return self.m_offset

    @offset.setter
    def offset(self, value: int):
        self.m_offset = value

    @property
    def sort_by(self) -> list:
        return self.m_sort_by

    @sort_by.setter
    def sort_by(self, value: dict):
        self.m_sort_by = value

    @property
    def object(self) -> str:
        return self.m_object

    def __str__(self) -> str:
        """
        Converts this :py:class:`Query` instance to its corresponding string representation.

        Returns:
            The corresponding string representation.
        """
        return "%(action)s%(attributes)s%(object)s%(filters)s%(limit)s%(offset)s%(sort_by)s" % {
            "action": action_to_str(self.action),
            "attributes": ", ".join(
                    sorted(set(self.attributes))
                ) if len(self.attributes) > 0 else " *",
            "object": " FROM %s" % self.object if self.object else "",
            "filters": " WHERE %s" % self.filters if self.filters else "",
            "limit": " LIMIT %s" % self.limit if self.limit else "",
            "offset": " OFFSET %s" % self.offset if self.offset  else "",
            "sort_by": " SORT BY %s" % ", ".join(
                    [
                        "%s %s" % (
                            attribute,
                            "ASC" if sort_asc == SORT_ASC else "DESC"
                        ) for attribute, sort_asc in self.sort_by.items()
                    ]
                ) if self.sort_by else "",
        }
