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

import re, string

def remove_accents(s :str) -> str:
    s = s.replace("š", "s") # Merci Ana :)
    s = s.replace("ć", "c") # La même :)
    s = s.replace("ç", "c")
    s = s.replace("á", "a")
    s = s.replace("à", "a")
    s = s.replace("ä", "a")
    s = s.replace("é", "e")
    s = s.replace("ê", "e")
    s = s.replace("è", "e")
    s = s.replace("ë", "e")
    s = s.replace("í", "i")
    s = s.replace("î", "i")
    s = s.replace("ï", "i")
    s = s.replace("ł", "l") # Merci Bartek
    s = s.replace("ö", "o")
    s = s.replace("ô", "o")
    s = s.replace("û", "u")
    s = s.replace("ü", "u")
    s = s.replace("ß", "ss")

    return s

def remove_ponctuation(s :str) -> str:
    translator = str.maketrans({key: None for key in string.punctuation})
    return s.translate(translator)

def to_canonic_string(s :str) -> str:
    s = s.lower()
    s = remove_accents(s)
    s = remove_ponctuation(s)
    s = re.sub("[$^,?!.:]", "", s)
    s = re.sub("\\[a-zA-Z0-9]+ ", "", s) # remove latex directive
    s = re.sub(" +", " ", s)
    #s = s.replace("data set", "dataset")
    #s = " ".join(s.split())          # remove useless spaces
    s = s.replace(" ", "")            # remove space. Avoid issues like "data set" and "dataset"
    return s

def to_canonic_fullname(s :str) -> str:
    s = s.lower()
    s = remove_accents(s)
    s = s.replace("-", " ")
    s = re.sub("\(.+\)", "", s)      # remove surnames
    s = re.sub("\&.*;", "", s)       # remove HTML
    s = re.sub("[a-zA-Z]+\.", "", s) # remove sigles
    s = " ".join(s.split())          # remove useless spaces
    return s

