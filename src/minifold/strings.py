#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import re
import string
import unicodedata

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


def to_international_chr(c: str) -> str:
    """
    Converts international characters to the corresponding character(s)
    in ``a-zA-Z``.

    Examples:
        >>> to_international_chr("ß")
        'ss'
        >>> to_international_chr("é")
        'e'

    Args:
        c (str): The input character.

    Returns:
        The corresponding characters(s).
    """
    return MAP_TO_INTERNATIONAL.get(c, c)


def to_international_string(s: str) -> str:
    """
    Converts a string involving international characters
    (see `:func:py:to_international_chr`) to the corresponding
    string.

    Example:
        >>> to_international_string("élève")
        'eleve'

    Args:
        s (str): The input string.

    Returns:
        The converted string.
    """
    translator = str.maketrans(MAP_TO_INTERNATIONAL)
    return s.translate(translator)


def remove_punctuation(s: str) -> str:
    """
    Replaces the punctuation characters by spaces.

    Example:
        >>> remove_punctuation("Example: a sentence, with punctuation."
        'Example  a sentence  with punctuation '

    Args:
        s (str): The input string.

    Returns:
        The converted string.
    """
    translator = str.maketrans({key: " " for key in string.punctuation})
    return s.translate(translator)


def remove_html_tags(s: str) -> str:
    """
    Removes the HTML tag from an HTML string.

    Example:
        >>> remove_html_tags("<a href='#'>A link</a> <u><i>italic underlined</i><u>")
        'A link bold italic underlined'

    Args:
        s (str): The input string.

    Returns:
        The converted string.
    """
    return re.sub("<[^>]+>", "", s)


def remove_html_escape_sequences(s: str) -> str:
    """
    Removes the HTML sequences.

    Example:
        >>> remove_html_escape_sequences("cha&icirc;ne")
        'chane'

    Args:
        s (str): The input string.

    Returns:
        The converted string.
    """
    return re.sub("[&].*;", "", s)


def remove_latex_escape_sequence(s: str) -> str:
    """
    Removes the latex sequences.

    Example:
        >>> remove_latex_escape_sequence("n\\oe ud")
        'nud'

    Args:
        s (str): The input string.

    Returns:
        The converted string.
    """
    return re.sub("\\\\[a-zA-Z0-9]+ ", "", s)


def to_canonic_string(s: str) -> str:
    """
    Canonizes a string.

    Args:
        s (str): The input string.

    Returns:
        The converted string.
    """
    s = s.lower()
    s = to_international_string(s)
    s = remove_punctuation(s)  # This includes '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    s = remove_latex_escape_sequence(s)
    s = s.replace(" ", "")  # Remove  spaces
    return s


def to_canonic_fullname(s: str) -> str:
    """
    Canonizes a fullname.

    Args:
        s (str): The input fullname.

    Returns:
        The converted fullname.
    """
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
    """
    Converts an unicode string to an UTF-8 string.

    Args:
        s (str): The input unicode string.

    Returns:
        The corresponding UTF-8 string.
    """
    return unicodedata.normalize("NFKD", s)
