#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import json
from .connector import Connector
from .singleton import Singleton

# Example of configuration

DEFAULT_MINIFOLD_CONFIG = """{
    "dblp:dagstuhl" : {
        "type" : "minifold.dblp.DblpConnector",
        "args" : {
            "dblp_api_url" : "https://dblp.dagstuhl.de"
        }
    },
    "dblp:uni-trier" : {
        "type" : "minifold.dblp.DblpConnector",
        "args" : {
            "dblp_api_url" : "https://dblp.uni-trier.de"
        }
    }
}"""


class Config(dict, metaclass=Singleton):
    """
    :py:class:`Config` is used to centralize the minifold
    configuration, possibly fetched from multiple files.

    Note this class inherits :py:class:`Singleton`, meaning
    that any instance of this class corresponds to the same
    instance.

    Each piece of configuration must be a dictionary mapping abitrary,
    where keys are (minifold gateway) arbitary names.
    Each gateway is mapped with a dictionnary which
    maps ``"key"`` with the appropriate :py:class:`Connector` type
    and ``"args"`` with the parameters to be passed to the corresponding constructor.

    These configuration pieces are typically stored in configuration
    file that resides in ``~/.minifold/conf``. By convention, each JSON
    file stored in this directory is named "gw_type:gw_name.json"
    where gw_type helps to understand the underlying minifold connector
    and gw_name identifies the nature of the data source.

    See :py:data:`DEFAULT_MINIFOLD_CONFIG`.

    Example:
        >>> from minifold.dblp import DblpConnector
        >>> config = Config()
        >>> config.loads(DEFAULT_MINIFOLD_CONFIG)
        >>> dblp1 = config.make_connector("dblp:dagstuhl")
        >>> dblp2 = config.make_connector("dblp:uni-trier")
    """
    def loads(self, s_json: str):
        """
        Populates the :py:class:`Config` instance from a JSON string.

        Args:
            s_json (str): A string containing JSON configuration.
        """
        self.update(json.loads(s_json))

    def load(self, stream):
        """
        Populates the :py:class:`Config` instance from an input stream
        (e.g., a read file descriptor) storing JSON data.

        Args:
            stream: The input JSON stream.
        """
        self.update(json.load(stream))

    def load_file(self, filename: str):
        """
        Populates the :py:class:`Config` instance from an JSON file.

        Args:
            filename (str): The path to the input JSON file.
                Example: ``~/.minifold/conf/gw_type:gw_name.json``.
        """
        with open(filename, "r") as f:
            self.load(f)

    def make_connector(self, name: str) -> Connector:
        """
        Makes a :py:class:`Connector` thanks to the :py:class:`Config` instance.

        Args:
            name (str): The name identifying the :py:class:`Connector` in
                the minifold configuration

        Raises:
            KeyError, if ``name`` is not in the :py:class:`Config` instance.

        Returns:
            The corresponding :py:class:`Connector` instance.
        """
        conf = self.get(name)
        if not conf:
            raise KeyError(
                "Config: Key [%s] not found. Known configuration are:\n%s\n" % (
                    name,
                    "\n\t".join([str(k) for k in self.keys()])
                )
            )
        type_name = conf["type"]
        cls = Connector.subclasses.get(type_name)
        if not cls:
            raise KeyError(
                "Config: Connector [%s] not found. Known connectors are:\n%s\n" % (
                    type_name,
                    "\n\t".join([str(k) for k in Connector.subclasses.keys()])
                )
            )
        kwargs = conf.get("args", dict())
        return cls(**kwargs)
