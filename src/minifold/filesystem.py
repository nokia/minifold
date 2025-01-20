#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

"""
This file gathers useful function to interact with the filesystem of the local storage.
"""

import datetime
import os
import errno
import shutil
import tempfile
from .log import Log


def rm(path: str, recursive: bool = False):
    """
    Removes a file (in shell: ``rm -f``).

    Args:
        path (str): A string containing the path of the file to remove.
        recursive (bool): Pass True to remove recursively a directory (in shell: ``rm -rf``).
    """
    if os.path.isdir(path):
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
    else:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


def ctime(path: str) -> datetime.datetime:
    """
    Retrieves the creation date of a file.

    Args:
        path (str): A string containing the path of the file.

    Returns:
        The corresponding datetime.
    """
    posix_time = os.path.getctime(path)
    return datetime.datetime.fromtimestamp(posix_time, datetime.UTC)


def mtime(path: str) -> datetime.datetime:
    """
    Retrieves the modification date of a file.

    Args:
        path (str): A string containing the path of the file.

    Returns:
        The corresponding datetime.
    """
    posix_time = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(posix_time, datetime.UTC)


def mkdir(directory: str):
    """
    Creates a directory (in shell: ``mkdir -p``).

    Args:
        directory (str): A String containing an absolute path.

    Raises:
        OSError: If the directory cannot be created.
    """
    # http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    try:
        if not os.path.exists(directory):
            Log.info("Creating '%s' directory" % directory)
        os.makedirs(directory)
    except FileExistsError:
        pass
    except OSError as e:  # Python >2.5
        if e.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise OSError("Cannot mkdir %s: %s" % (directory, e))


def check_writable_directory(directory: str):
    """
    Tests whether a directory is writable. If not, an expection is raised.

    Args:
        directory (str): A String containing an absolute path.

    Raises:
        RuntimeError: If the directory does not exists or isn't writable.
    """
    if not os.path.exists(directory):
        raise RuntimeError("Directory '%s' does not exists" % directory)
    if not os.access(directory, os.W_OK | os.X_OK):
        raise RuntimeError("Directory '%s' is not writable" % directory)
    try:
        with tempfile.TemporaryFile(dir=directory):
            pass
    except Exception as e:
        raise RuntimeError("Cannot write into directory '%s': %s" % (directory, e))


def find(dir_name: str) -> list:
    """
    Lists the regular files in a stored in given directory or one of its subdirectories
    (in shell: ``find -type f dir_name``).

    Args:
        dir_name (str): A String corresponding to an existing directory.

    Returns:
        A list of strings, each of them corresponding to a file.
    """
    filenames = list()
    files = os.listdir(dir_name)
    for base_name in files:
        cur_path = os.path.join(dir_name, base_name)
        if os.path.isdir(cur_path):
            filenames += find(cur_path)
        else:
            filenames.append(cur_path)
    return filenames
