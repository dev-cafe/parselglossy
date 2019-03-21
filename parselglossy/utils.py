#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2019 Roberto Di Remigio, Radovan Bast, and contributors.
#
# This file is part of parselglossy.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For information on the complete list of contributors to the
# parselglossy library, see: <http://parselglossy.readthedocs.io/>
#

# -*- coding: utf-8 -*-
"""Common utilities."""

import json
import re
from functools import reduce
from string import ascii_letters, digits
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

JSONDict = Dict[str, Any]

truthy = ["TRUE", "ON", "YES", "Y"]
"""List[str]: List of true-like values."""
falsey = ["FALSE", "OFF", "NO", "N"]
"""List[str]: List of false-like values."""

printable = ascii_letters + digits + r"!#$%&*+-./:;<>?@^_|~"
"""str: Custom printable character set.

The printable character set is the standard set in `string.printable` minus
"\'(),=[\\]`{} and all whitespace characters.
"""


class ComplexEncoder(json.JSONEncoder):
    """JSON encoder for complex numbers."""

    def default(self, obj):
        if isinstance(obj, complex):
            return {"__complex__": [obj.real, obj.imag]}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def as_complex(dct):
    """JSON decoder for complex numbers."""
    if "__complex__" in dct:
        return complex(dct["__complex__"][0], dct["__complex__"][1])
    return dct


RunCallable = Callable[[Any, str], Tuple[str, Any]]

ScalarTypes = Union[bool, str, int, float, complex]

allowed_scalar_types = ["str", "int", "float", "complex", "bool"]


def _type_check_scalar(value: ScalarTypes, expected_type: str) -> bool:
    return type(value).__name__ == expected_type


ListTypes = Union[List[bool], List[str], List[int], List[float], List[complex]]

allowed_list_types = ["List[{}]".format(t) for t in allowed_scalar_types]


def _type_check_list(value: ListTypes, expected_type: str) -> bool:
    # make sure that value is actually a list
    if type(value).__name__ == "list":
        # iterate over each element of the list
        # and check whether it matches T
        type_checks = all((_type_check_scalar(x, expected_type) for x in value))
    else:
        type_checks = False

    return type_checks


AllowedTypes = Union[ScalarTypes, ListTypes]

allowed_types = allowed_scalar_types + allowed_list_types


def type_matches(value: AllowedTypes, expected_type: str) -> Optional[bool]:
    """Checks whether a value is of the expected type.

    Parameters
    ----------
    value : AllowedTypes
      Value whose type needs to be checked
    expected_type : str

    Notes
    -----
    Allowed types T are: `str`, `int`, `float`, `complex`, `bool`,
    as well as `List[T]`.

    Returns
    -------
    True if value has the type expected_type, otherwise False.

    Raises
    ------
    ValueError
        If expected_type is not among the allowed types.
    """

    # first verify whether expected_type is allowed
    if expected_type not in allowed_types:
        raise ValueError("could not recognize expected_type: {}".format(expected_type))

    expected_type_is_list = re.search(r"^List\[(\w+)\]$", expected_type)

    if expected_type_is_list is not None:
        return _type_check_list(value, expected_type_is_list.group(1))  # type: ignore
    else:
        return _type_check_scalar(value, expected_type)  # type: ignore


type_fixers = {
    "bool": bool,
    "complex": complex,
    "float": float,
    "int": int,
    "str": str,
    "List[bool]": lambda x: list(map(bool, x)),
    "List[complex]": lambda x: list(map(complex, x)),
    "List[float]": lambda x: list(map(float, x)),
    "List[int]": lambda x: list(map(int, x)),
    "List[str]": lambda x: list(map(str, x)),
}  # type: Dict[str, Callable[[Any], Any]]
"""Dict[str, Callable[[Any], Any]]: dictionary holding functions for type fixation."""


def plain(result: Any, t: str = "") -> Tuple[str, Any]:
    return "", result


def with_type_checks(result: Any, t: str) -> Tuple[str, Optional[Any]]:
    if type_matches(result, t):
        msg = ""
        result = type_fixers[t](result)
    else:
        msg = "Actual ({0}) and declared ({1}) types do not match.".format(
            type(result).__name__, t
        )
        result = None
    return msg, result


def run_callable(
    f: str, d: JSONDict, *, t: Optional[str] = None
) -> Tuple[str, Optional[Any]]:
    """Run a callable encoded as a string.

    A callable is any function of the input tree.

    Parameters
    ----------
    f : str
        Callable to checked as a string
    d : JSONDict
        The input `dict`.
    t : str
        Expected type.
    post : RunCallable
        Actions to run after calling ``eval``

    Returns
    -------
    retval : Tuple[str, Optional[Any]]
        The error message, if any, and the result of the callable, if any.

    Notes
    -----
    The input tree is called ``user``.
    """

    closure = "lambda user: "
    if t is None:
        post = plain
        closure += "{}"
    else:
        post = with_type_checks
        if t == "str":
            closure += "'{}'"
        elif t == "complex":
            closure += "complex('{}'.replace(' ', ''))"
        elif t == "List[complex]":
            closure += "list(map(lambda x: complex(x.replace(' ', '')), {}))"
        else:
            closure += "{}"

    postfix = "in closure '{}'.".format(f)

    try:
        result = eval(closure.format(f))(d)
        msg, result = post(result, t)
    except KeyError as e:
        msg = "KeyError {} {:s}".format(e, postfix)
        result = None
    except SyntaxError as e:
        msg = "SyntaxError {} {:s}".format(e, postfix)
        result = None
    except TypeError as e:
        msg = "TypeError {} {:s}".format(e, postfix)
        result = None
    except NameError as e:
        msg = "NameError {} {:s}".format(e, postfix)
        result = None

    return msg, result


def location_in_dict(*, address: Tuple[str], dict_name: str = "user") -> str:
    """Convert tuple of keys of a ``JSONDict`` to its representation in code.

    For example, given ``("a", "b", "c")`` returns the string ``user['a']['b']['c']``.

    Parameters
    ----------
    address : Tuple[str]
    dict_name : str

    Returns
    -------
    where : str
    """
    return reduce(lambda x, y: x + "['{}']".format(y), address, "user")
