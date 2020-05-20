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

import datetime, os, errno, shutil, tempfile

from .log import Log

def rm(path :str, recursive :bool = False):
    """
    Remove a file (rm -f).
    Args:
        path: A string containing the path of the file to remove.
        recursive: Pass True to remove recursively a directory (rm -rf).
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

def ctime(path) -> datetime.datetime:
    """
    Retrieve the creation date of a file.
    Args:
        path: A string containing the path of the file to remove.
    Returns:
        The corresponding datetime.
    """
    posix_time = os.path.getctime(path)
    return datetime.datetime.utcfromtimestamp(posix_time)

def mtime(path) -> datetime.datetime:
    """
    Retrieve the modification date of a file.
    Args:
        path: A string containing the path of the file to remove.
    Returns:
        The corresponding datetime.
    """
    posix_time = os.path.getmtime(path)
    return datetime.datetime.utcfromtimestamp(posix_time)

def mkdir(directory):
    """
    Create a directory (mkdir -p).
    Args:
        directory: A String containing an absolute path.
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
    except OSError as e: # Python >2.5
        if e.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise OSError("Cannot mkdir %s: %s" % (directory, e))

def check_writable_directory(directory):
    """
    Tests whether a directory is writable.
    Args:
        directory: A String containing an absolute path.
    Raises:
        RuntimeError: If the directory does not exists or isn't writable.
    """
    if not os.path.exists(directory):
        raise RuntimeError("Directory '%s' does not exists" % directory)
    if not os.access(directory, os.W_OK | os.X_OK):
        raise RuntimeError("Directory '%s' is not writable" % directory)
    try:
        with tempfile.TemporaryFile(dir = directory):
            pass
    except Exception as e:
        raise RuntimeError("Cannot write into directory '%s': %s" % (directory, e))

def find(dir_name :str) -> list:
    """
    List regular files in a stored in given directory or one of its subdirectories.
    Args:
        dir_name: A String corresponding to an existing directory.
    Returns:
        A list of String, each of them corresponding to a file.
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
