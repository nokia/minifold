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

import json, sys
from minifold.connector import Connector
from minifold.singleton import Singleton

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

# Usage:
# from minifold.dblp import DblpConnector
# config = Config()
# config.loads(DEFAULT_MINIFOLD_CONFIG)
# dblp1 = config.make_connector("dblp:dagstuhl")
# dblp2 = config.make_connector("dblp:uni-trier")

class Config(dict, metaclass=Singleton):
    def loads(self, s_json :str):
        self.update(json.loads(s_json))

    def load(self, stream):
        self.update(json.load(stream))

    def load_file(self, filename :str):
        with open(filename, "r") as f:
            self.load(f)

    def make_connector(self, name :str):
        conf = self.get(name)
        if not conf:
            raise KeyError(
                "Config: Key [%s] not found. Known configuration are:\n%s\n" % (
                    name,
                    "\n\t".join([str(k) for k in self.keys()])
                )
            )
        type = conf["type"]
        cls = Connector.subclasses.get(type)
        if not cls:
            raise KeyError(
                "Config: Connector [%s] not found. Known connectors are:\n%s\n" % (
                    type,
                    "\n\t".join([str(k) for k in Connector.subclasses.keys()])
                )
            )
        kwargs = conf.get("args", dict())
        return cls(**kwargs)

