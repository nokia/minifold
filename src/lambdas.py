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

from copy       import deepcopy
from .connector import Connector
from .query     import Query

def find_lambda_dependencies(func) -> set:
    entry = dict()
    while True:
        try:
            val = func(entry)
        except KeyError as e:
            needed_key = e.args[0]
            entry[needed_key] = None
            continue
        except Exception as e:
            pass
        break
    return set(entry.keys())

def find_lambdas_dependencies(map_lambdas :dict) -> dict:
    return {attr : find_lambda_dependencies(func) for attr, func in map_lambdas.items()}

def lambdas(map_lambdas :dict, entries :list, attributes :set = None) -> list:
    # Be sure that the result is deterministic without regards each
    # lambda is processed.
    # Ex: map_lambdas = {"x" : lambda e: 10 + e["x"]} is OK
    # Ex: map_lambdas = {"x" : lambda e: 10 + e["x"] + e["y"]} is OK
    # Ex: map_lambdas = {
    #       "x" : lambda e: 10 + e["x"] + e["y"]
    #       "y" : lambda e: 10 + e["y"]
    #     } is not OK because e["y"] is ambiguous when executing the lambda related to "x".
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
    def __init__(self, map_lambdas :dict, child :Connector, map_dependencies :dict = None):
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
        return self.m_child

    def attributes(self, object :str) -> set:
        return self.m_child.attributes(object) | set(self.m_map_lambdas.keys())

    def find_needed_attributes(self, attributes :set) -> set:
        ret = set()
        for attribute in attributes:
            needed_attributes = self.m_map_dependencies.get(attribute, set([attribute]))
            ret |= needed_attributes
        return ret

    def query(self, q :Query) -> list:
        super().query(q)
        q_child = deepcopy(q)

        if q.attributes or q.filters:
            where_attributes = self.find_needed_attributes(find_lambda_dependencies(q.filters))

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
                q_child.attributes = list((select_attributes | where_attributes) - lambdas_attributes)

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
