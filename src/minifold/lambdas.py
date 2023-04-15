#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from copy import deepcopy
from .connector import Connector
from .query import Query

def find_lambda_dependencies(func: callable) -> set:
    """
    Infers the keys needed by a function processing a dictionary
    to not trigger :py:class:`KeyError` exception.

    Args:
        func (callable): A function taking a dictionary in parameter.

    Returns:
        The keys needed by ``func`` to process a dictionary.
    """
    entry = dict()
    while True:
        try:
            _ = func(entry)
        except KeyError as e:
            needed_key = e.args[0]
            entry[needed_key] = None
            continue
        except Exception:
            pass
        break
    return set(entry.keys())

def find_lambdas_dependencies(map_lambdas: dict) -> dict:
    """
    Infers the keys needed by several functions that outputs a specific
    entry key when processing an input entry so that no
    :py:class:`KeyError` exception is raised.

    Args:
        map_lambdas (dict): A dictionary that maps key
            (existing or new) key attributes with a function
            processing an input entry.

    Returns:
        The keys needed by the functions involved in ``map_lambdas.values()``
        to process a minifold entry
    """
    return {
        attr: find_lambda_dependencies(func)
        for (attr, func) in map_lambdas.items()
    }

def lambdas(map_lambdas: dict, entries: list, attributes: set = None) -> list:
    """
    Be sure that the result is deterministic without regards each
    lambda is processed.

    Examples:
        >>> map_lambdas = {"x": lambda e: 10 + e["x"]} # OK
        >>> map_lambdas = {"x": lambda e: 10 + e["x"] + e["y"]} # OK
        >>> map_lambdas = {
        ...     "x": lambda e: 10 + e["x"] + e["y"],
        ...     "y": lambda e: 10 + e["y"]
        ... } # not OK because e["y"] is ambiguous.
    """
    attrs = set(map_lambdas.keys())
    if attributes:
        attrs &= set(attributes)
    for entry in entries:
        for attr, func in map_lambdas.items():
            if attr in attrs:
                try:
                    entry[attr] = func(entry)
                except KeyError:
                    entry[attr] = None
    return entries

class LambdasConnector(Connector):
    """
    The :py:class:`LambdasConnector` class is used to apply the `lambdas` function
    in the middle of a minifold pipeline. It allows to craft or reshape a flow
    of minifold entries on-the-fly.
    """
    def __init__(self, map_lambdas: dict, child: Connector, map_dependencies: dict = None):
        """
        Constructor.

        Args:
            map_lambdas (dict): A dictionary that maps key
                (existing or new) key attributes with a function
                processing an input entry.
            child (Connector): The child minifold :py:class:`Connector`
                instance.
        """
        # Ensure there is no cyclic dependency (see lambdas())
        super().__init__()
        self.m_child = child
        self.m_map_lambdas = map_lambdas

        # If no attribute dependency is provided, use find_lambda_dependencies heuristic.
        self.m_map_dependencies = map_dependencies \
            if map_dependencies is not None \
            else find_lambdas_dependencies(map_lambdas)

    @property
    def child(self) -> Connector:
        """
        Accessor to the child minifold :py:class:`Connector` instance.

        Returns:
            The child minifold :py:class:`Connector` instance.
        """
        return self.m_child

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`LambdasConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return self.m_child.attributes(object) | set(self.m_map_lambdas.keys())

    def find_needed_attributes(self, attributes: set) -> set:
        """
        Finds the attribute that are needed to process a set of attributes of interest.

        Args:
            attributes (set): The attributes of interest.

        Returns:
            The corresponding needed attributes.
        """
        ret = set()
        for attribute in attributes:
            needed_attributes = self.m_map_dependencies.get(attribute, {attribute})
            ret |= needed_attributes
        return ret

    def query(self, q: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """

        super().query(q)
        q_child = deepcopy(q)

        if q.attributes or q.filters:
            where_attributes = self.find_needed_attributes(
                find_lambda_dependencies(q.filters)
            )

            if q.attributes:
                child_attributes = self.m_child.attributes(None)
                select_attributes  = self.find_needed_attributes(set(q.attributes))
                # Remove lambda-specific attributes
                lambdas_attributes = set(self.m_map_lambdas.keys()) - {
                    dep_attr
                    for attr in q.attributes
                    for dep_attr in self.m_map_dependencies.get(attr, set())
                    if dep_attr in child_attributes
                }
                q_child.attributes = list(
                    (select_attributes | where_attributes) - lambdas_attributes
                )

            if where_attributes:
                # If the filter involves at least one attribute of the LambdasConnector
                # the filter is not forwarded to the child node, and the filtering is
                # achieved locally achieved locally to this LambdasConnector.
                # As a sequel, the child node may return entries that could be filtered
                # thanks to the self.reshape_entries method.
                q_child.filters = None

        entries = self.reshape_entries(
            q,
            lambdas(
                self.m_map_lambdas,
                self.child.query(q_child),
                q.attributes
            )
        )

        return self.answer(q, entries)
