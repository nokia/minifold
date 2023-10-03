#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

from minifold.config import Config
from minifold.connector import Connector
from minifold.log import Log


Log.enable_print = True

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


def test_minifold_config_singleton():
    config = Config()
    config2 = Config()
    assert config == config2


def test_minifold_config_loads():
    config = Config()
    config.loads(DEFAULT_MINIFOLD_CONFIG)
    k1 = "dblp:dagstuhl"
    k2 = "dblp:uni-trier"
    assert set(config.keys()) == {k1, k2}

    from minifold.dblp import DblpConnector
    Log.debug(Connector.subclasses)
    dblp1 = config.make_connector(k1)
    assert isinstance(dblp1, DblpConnector)
    dblp2 = config.make_connector(k2)
    assert isinstance(dblp2, DblpConnector)
