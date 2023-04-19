#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

class Singleton(type):
    """
    The :py:class:`Singleton` allows to define singleton classes, i.e.
    classes that can be instantiated at most once.

    >>> class MyClass(metaclass=Singleton): pass
    >>> x = MyClass()
    >>> y = MyClass()
    >>> x is y
    True

    Based on this `thread <https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python>`__.
    """
    s_instances = dict()

    def __call__(cls, *args, **kwargs):
        """
        Functor method.

        Args:
            cls: The class using the singleton pattern.
            *args: The args of the class constructor of ``cls``.
            **kwargs: The kwargs of the class constructor of ``cls``.

        Returns:
            The singleton corresponding to ``cls``.
        """
        if cls not in cls.s_instances:
            cls.s_instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.s_instances[cls]
