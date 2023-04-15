#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

try:
    from ldap3                  import Server, Connection, SUBTREE, ALL_ATTRIBUTES, ALL
    from ldap3.core.exceptions  import LDAPInvalidFilterError
except ImportError as e:
    from .log import Log
    Log.warning(
        "Please install ldap3.\n"
        "  APT: sudo apt install python3-ldap3\n"
        "  PIP: sudo pip3 install --upgrade ldap3\n"
    )
    raise e

import operator
from .connector import Connector
from .query import Query, ACTION_READ
from .binary_predicate import BinaryPredicate
from .log import Log

class LdapConnector(Connector):
    def __init__(
        self,
        ldap_host: str,
        ldap_user: str = None,
        ldap_password: str = None,
        ldap_use_ssl: bool = None
    ):
        """
        Constructor.

        Args:
            ldap_host (str): The FQDN or the IP of the server (e.g., "my-ldap.firm.com").
            ldap_user (str): The LDAP login used to connect to the server.
            ldap_password (str): The LDAP password of ``ldap_user``.
            ldap_use_ssl (bool): Pass ``True`` if the connection to the server must
                be established using SSL, ``False`` or ``None`` otherwise.
        """
        super().__init__()
        self.m_server     = Server(ldap_host, use_ssl=ldap_use_ssl, get_info=ALL)
        self.m_connection = Connection(self.m_server, ldap_user, ldap_password)
        self.m_connection.bind()

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`LdapConnector` instance.

        Args:
            object (str): The name of the collection.

        Returns:
            The set of corresponding attributes.
        """
        return {str(key) for key in self.m_connection.server.schema.attribute_types.keys()}

    def __enter__(self):
        """
        Method called when entering a ``with LdapConnector(...):`` block.
        """
        self.m_connection.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        """
        Method called when leaving a ``with LdapConnector(...):`` block.
        """
        self.m_connection.unbind()

    @staticmethod
    def operator_to_ldap(op) -> str:
        """
        Converts a minifold operator to the corresponding LDAP operator.

        Args:
            operator: The operator to be converted.

        Returns:
            The corresponding LDAP string.
        """
        if op == operator.__eq__:
            return "="
        elif op == operator.__and__:
            return "&"
        elif op == operator.__or__:
            return "|"
        # elif op == "<=" or op == ">=" or op == "<" or op == ">" or op == "~": return op
        else:
            raise RuntimeError("LdapConnector::operator_to_ldap: op = %s not supported" % op)

    @staticmethod
    def binary_predicate_to_ldap(p: BinaryPredicate) -> str:
        """
        Converts a :py:class:`BinaryPredicate` to the corresponding LDAP predicate.

        Args:
            p (BinaryPredicate): A :py:class:`BinaryPredicate` instance.

        Returns:
            The corresponding LDAP predicate.
        """

        if p.operator in ["&&", "||"]:
            # See http://ldap3.readthedocs.io/searches.html
            fmt = "(%(operator)s%(left)s%(right)s)"
        else:
            fmt = "%(left)s%(operator)s%(right)s"
        return fmt % {
            "left": LdapConnector.operand_to_ldap(p.left),
            "operator": LdapConnector.operator_to_ldap(p.operator),
            "right": LdapConnector.operand_to_ldap(p.right)
        }

    @staticmethod
    def operand_to_ldap(operand: str) -> str:
        """
        Converts a minifold operand to the corresponding LDAP operand.

        Args:
            operand (str): The operand to be converted.

        Returns:
            The corresponding string.
        """
        if isinstance(operand, BinaryPredicate):
            return "(%s)" % LdapConnector.binary_predicate_to_ldap(operand)
        elif isinstance(operand, (int, float, str)):
            # Do not add '...' or "..." for str
            return operand
        else:
            raise RuntimeError("Operand type not supported %s" % type(operand))

    @staticmethod
    def literal_from_ldap(b: bytes) -> str:
        """
        Converts a LDAP literal to the corresponding string.

        Args:
            b (bytes): The input literal.

        Returns:
            The corresponding string.
        """
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
    def sanitize_dict(d: dict) -> dict:
        """
        Reshapes the dictionary returned by a LDAP query to a minifold entry.

        Args:
            d (dict): The input dict.

        Returns:
            The corresponding sanitized dictionary.
        """
        sane = False
        for k,v in d.items():
            # raw values are always list
            if len(v) == 1:
                d[k] = LdapConnector.literal_from_ldap(v[0])
            else:
                d[k] = [LdapConnector.literal_from_ldap(x) for x in v]
            if not d[k]:
                d[k] = None
            else:
                sane = True
        return d if sane else dict()

    def query(self, q: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """
        super().query(q)
        entries = list()

        if q.action == ACTION_READ:
            if len(q.attributes) == 0:
                attributes = ALL_ATTRIBUTES
            else:
                attributes = q.attributes

            if q.filters is None:
                keep_if = "(objectClass=*)"
            else:
                keep_if = LdapConnector.operand_to_ldap(q.filters)

            try:
                if attributes != ALL_ATTRIBUTES:
                    attributes = set(attributes) & self.attributes(q.object)
                Log.info("--> LDAP: dn = %s filter = %s attributes = %s"
                    % (
                        q.object,
                        keep_if,
                        attributes
                    )
                )
                self.m_connection.search(
                    q.object,
                    keep_if,
                    search_scope = SUBTREE,
                    attributes = attributes
                )
            except LDAPInvalidFilterError as e:
                Log.error("LdapConnector::query: Invalid filter: %s" % keep_if)
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
