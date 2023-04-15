#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

"""
This file gathers utilities related to ipython Jupyter notebooks.
"""

def in_ipynb() -> bool:
    """
    Tests whether the code is running inside a Jupyter Notebook.

    Returns:
        ``True`` iff the code is running inside a Jupyter Notebook.
    """
    try:
        from IPython import get_ipython
        return str(type(get_ipython())) == "<class 'ipykernel.zmqshell.ZMQInteractiveShell'>"
    except NameError:
        return False
    except ImportError:
        return False
