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

try:
    from ldap3                  import Server, Connection, SUBTREE, ALL_ATTRIBUTES, ALL
    from ldap3.core.exceptions  import LDAPInvalidFilterError
except ImportError:
    raise ImportError("LdapConnector requires python3-ldap3: please run: apt-get install python3-ldap3")

import operator
from .connector             import Connector
from .query                 import Query, ACTION_READ
from .binary_predicate      import BinaryPredicate
from .log                   import Log

class LdapConnector(Connector):
    def __init__(self, ldap_host, ldap_user = None, ldap_password = None, ldap_use_ssl = None):
        super().__init__()
        self.m_server     = Server(ldap_host, use_ssl = ldap_use_ssl, get_info = ALL)
        self.m_connection = Connection(self.m_server, ldap_user, ldap_password)
        self.m_connection.bind()

    def attributes(self, object :str) -> set:
        return {str(key) for key in self.m_connection.server.schema.attribute_types.keys()}

    def __enter__(self):
        self.m_connection.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.m_connection.unbind()

    @staticmethod
    def operator_to_ldap(op :str) -> str:
        if   op == operator.__eq__:  return "="
        elif op == operator.__and__: return "&"
        elif op == operator.__or__:  return "|"
        #elif op == "<=" or op == ">=" or op == "<" or op == ">" or op == "~": return op
        raise RuntimeError("LdapConnector::operator_to_ldap: op = %s not supported" % op)

    @staticmethod
    def binary_predicate_to_ldap(p :BinaryPredicate) -> str:
        if p.operator in ["&&", "||"]:
            # See http://ldap3.readthedocs.io/searches.html
            format = "(%(operator)s%(left)s%(right)s)"
        else:
            format = "%(left)s%(operator)s%(right)s"
        return format % {
            "left"     : LdapConnector.operand_to_ldap(p.left),
            "operator" : LdapConnector.operator_to_ldap(p.operator),
            "right"    : LdapConnector.operand_to_ldap(p.right)
        }

    @staticmethod
    def operand_to_ldap(operand) -> str:
        if isinstance(operand, BinaryPredicate):
            return "(%s)" % LdapConnector.binary_predicate_to_ldap(operand)
        elif isinstance(operand, (int, float, str)):
            # Do not add '...' or "..." for str
            return operand
        else:
            raise RuntimeError("Operand type not supported %s" % type(operand))

    @staticmethod
    def literal_from_ldap(b :bytes):
        try:
            return int(b)
        except ValueError:
            pass
        try:
            return float(b)
        except ValueError:
            pass
        try:
            return b.decode("utf-8")
        except ValueError:
            pass
        return b

    @staticmethod
    def sanitize_dict(d :dict) -> dict:
        sane = False
        for k,v in d.items():
            # raw values are always list
            if len(v) == 1:
                d[k] = LdapConnector.literal_from_ldap(v[0])
            else:
                d[k] = [LdapConnector.literal_from_ldap(x) for x in v]
            if d[k] == []:
                d[k] = None
            else:
                sane = True
        return d if sane == True else dict()

    def query(self, q :Query):
        super().query(q)
        entries = list()

        if q.action == ACTION_READ:
            if len(q.attributes) == 0:
                attributes = ALL_ATTRIBUTES
            else:
                attributes = q.attributes

            if q.filters == None:
                filter = "(objectClass=*)"
            else:
                filter = LdapConnector.operand_to_ldap(q.filters)

            try:
                if attributes != ALL_ATTRIBUTES:
                    attributes = set(attributes) & self.attributes(q.object)
                Log.info("--> LDAP: dn = %s filter = %s attributes = %s" % (q.object, filter, attributes))
                self.m_connection.search(
                    q.object,
                    filter,
                    search_scope = SUBTREE,
                    attributes = attributes
                )
            except LDAPInvalidFilterError as e:
                Log.error("LdapConnector::query: Invalid filter: %s" % filter)
                raise e

            for entry in self.m_connection.response:
                entry = LdapConnector.sanitize_dict(entry["raw_attributes"])
                if len(entry) > 0:
                    # Fix missing keys
                    if len(q.attributes) > 0:
                        for missing_key in (set(q.attributes) - set(entry.keys())):
                            entry[missing_key] = None
                    entries.append(dict(entry))
        else:
            raise RuntimeError("Not implemented")
        return self.answer(q, entries)


