# =======================================================================
#
#  This file is part of WebWidgets, a Python package for designing web
#  UIs.
#
#  You should have received a copy of the MIT License along with
#  WebWidgets. If not, see <https://opensource.org/license/mit>.
#
#  Copyright(C) 2025, mlaasri
#
# =======================================================================

from typing import *
import re


def validate_css_identifier(identifier: str) -> None:
    """Checks if the given identifier is a valid identifier token according to
    the CSS syntax rules and raises an exception if not.

    An identifier token is a sequence of characters that can be used as part of
    a CSS rule, like a class name or an ID. The concept essentially corresponds
    to that of an `ident-token` in the official CSS specification.

    This function enforces the following rules:
    - the identifier must only contain letters (`a-z`, `A-Z`), digits (`0-9`),
      underscores (`_`), and hyphens (`-`)
    - the identifier must start with either a letter, an underscore, or a
      double hyphen (`--`)

    Note that this function imposes stricter rules on identifier tokens than
    the official CSS specification - more precisely, than chapter 4 of the CSS
    Syntax Module Level 3 (see source:
    https://www.w3.org/TR/css-syntax-3/#tokenization - note that this chapter
    remains the same in the current draft for Level 4). For example, this
    function does not allow escaped special characters nor identifier tokens
    starting with a single hyphen whereas the specification does.

    :param identifier: The string to be validated as an identifier token.
    :type identifier: str
    :raises ValueError: If the identifier is not a valid identifier token and
        does not respect the specified rules.
    """
    # Check if identifier starts with anything else than a letter, an
    # underscore, or a double hyphen
    if not re.match(r'^[a-zA-Z_]+|--', identifier):
        raise ValueError("CSS identifier must start with either a letter, an "
                         "underscore, or a double hyphen (`--`), but got: "
                         f"'{identifier}'")

    # Check if identifier contains invalid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', identifier):
        invalid_chars = re.findall('[^a-zA-Z0-9_-]', identifier)
        raise ValueError("Invalid character(s) in CSS idenfitier "
                         f"'{identifier}': {', '.join(invalid_chars)}\n"
                         "Only letters, digits, hyphens, and underscores are "
                         "allowed.")


def validate_html_class(class_attribute: str) -> None:
    """Checks if the given HTML class attribute is valid and raises an
    exception if not.

    This function enforces the following rules:
    - the class attribute cannot start nor end with a space
    - the class attribute cannot contain double spaces
    - each class in the attribute must be a valid CSS identifier, as validated
      by the :py:func:`validate_css_identifier` function.

    Note that this function imposes stricter rules than rule 2.3.7 of the HTML5
    specification (see source:
    https://html.spec.whatwg.org/#set-of-space-separated-tokens). For example,
    it does not allow for leading nor trailing spaces whereas the specification
    does.

    :param class_attribute: The HTML class attribute to be validated.
    :type class_attribute: str
    :raises ValueError: If the class attribute is invalid and does not respect
        the specified rules.
    """
    # Allow for empty attribute
    if not class_attribute:
        return

    # Check if the class attribute starts or ends with a space
    if class_attribute.startswith(' ') or class_attribute.endswith(' '):
        raise ValueError("Class attribute cannot start nor end with a space, "
                         f"but got: '{class_attribute}'")

    # Check for double spaces in the class attribute
    if '  ' in class_attribute:
        raise ValueError("Class attribute cannot contain double spaces, "
                         f"but got: '{class_attribute}'")

    # Check each class individually
    for c in class_attribute.split(' '):
        validate_css_identifier(c)
