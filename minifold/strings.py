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

import re, string, unicodedata

MAP_TO_INTERNATIONAL = {
    # Upper case
    "Á": "A",
    "À": "A",
    "Ä": "A",
    "Ć": "C",
    "Ç": "C",
    "Đ": "D",
    "É": "E",
    "Ê": "E",
    "È": "E",
    "Ë": "E",
    "Í": "I",
    "Î": "I",
    "Ï": "I",
    "Ł": "L",
    "Ö": "O",
    "Ô": "O",
    "Û": "U",
    "Ü": "U",
    "Š": "S",
    # Lower case
    "á": "a",
    "à": "a",
    "ä": "a",
    "ć": "c",
    "ç": "c",
    "đ": "d",
    "é": "e",
    "ê": "e",
    "è": "e",
    "ë": "e",
    "í": "i",
    "î": "i",
    "ï": "i",
    "ł": "l",
    "ö": "o",
    "ô": "o",
    "û": "u",
    "ü": "u",
    "š": "s",
    # Only lower
    "ß": "ss",
}

def to_international_chr(c: chr) -> chr:
    return MAP_TO_INTERNATIONAL.get(c, c)

def to_international_string(s: str) -> str:
    translator = str.maketrans(MAP_TO_INTERNATIONAL)
    return s.translate(translator)

def remove_punctuation(s: str) -> str:
    translator = str.maketrans({key: " " for key in string.punctuation})
    return s.translate(translator)

def remove_html_tags(s: str) -> str:
    return re.sub("<[^>]+>", "", s)

def remove_html_escape_sequences(s: str) -> str:
    return re.sub("[&].*;", "", s)

def remove_latex_escape_sequence(s: str) -> str:
    return re.sub("\\\\[a-zA-Z0-9]+ ", "", s)

def to_canonic_string(s: str) -> str:
    s = s.lower()
    s = to_international_string(s)
    s = remove_punctuation(s)  # This includes '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    s = remove_latex_escape_sequence(s)
    s = s.replace(" ", "")  # Remove  spaces
    return s

def to_canonic_fullname(s: str) -> str:
    s = to_international_string(s.lower())
    s = s.replace("-", " ")
    s = re.sub("[(].+[)]", "", s)      # Remove surnames
    s = remove_latex_escape_sequence(s)
    s = remove_html_tags(s)
    s = remove_html_escape_sequences(s)
    s = re.sub("[a-zA-Z]+[.]", "", s)  # Remove sigles
    s = " ".join(s.split())            # Remove useless spaces
    return s

def unicode_to_utf8(s: str) -> str:
    return unicodedata.normalize("NFKD", s)
