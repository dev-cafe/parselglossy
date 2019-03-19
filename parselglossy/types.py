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

import re
from typing import List, Tuple, Union

from .exceptions import Error, ValidationError, collate_errors
from .utils import JSONDict

ScalarTypes = Union[bool, str, int, float, complex]


def _type_check_scalar(value: ScalarTypes, expected_type: str) -> bool:
    return type(value).__name__ == expected_type


ListTypes = Union[List[bool], List[str], List[int], List[float], List[complex]]


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


def type_matches(value: AllowedTypes, expected_type: str) -> bool:
    """Checks whether a value is of the expected type.

    Parameters
    ----------
    value: Any
      Value whose type needs to be checked
    expected_type: AllowedTypes

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
    allowed_basic_types = ["str", "int", "float", "complex", "bool"]
    allowed_list_types = ["List[{}]".format(t) for t in allowed_basic_types]
    allowed_types = allowed_basic_types + allowed_list_types

    # first verify whether expected_type is allowed
    if expected_type not in allowed_types:
        raise ValueError("could not recognize expected_type: {}".format(expected_type))

    expected_type_is_list = re.search(r"^List\[(\w+)\]$", expected_type)

    if expected_type_is_list is not None:
        return _type_check_list(value, expected_type_is_list.group(1))
    else:
        return _type_check_scalar(value, expected_type)


type_fixers = {"bool": bool, "complex": complex, "float": float, "int": int, "str": str}
tmp = {
    "List[{:s}]".format(k): lambda x: list(map(v, x)) for k, v in type_fixers.items()
}
type_fixers.update(tmp)
"""Dict[str, Callable[[Any], Any]: dictionary holding functions for type fixation."""


def typenade(incoming: JSONDict, types: JSONDict) -> JSONDict:
    """Checks types of input values for a merge input ``dict``.

    Parameters
    ----------
    incoming: JSONDict
        The input `dict`. This is supposed to be the one obtained by merging
        user and template `dict`-s.
    types: JSONDict
        Types of all keywords in the input. Generated from :func:`view_by_types`.

    Returns
    -------
    outgoing: JSONDict
        A dictionary with all values type checked.

    Raises
    ------
    :exc:`ValidationError`

    Notes
    -----
    This is porcelain over :func:`_typenade`.
    """
    outgoing, errors = _typenade(incoming, types)

    if errors:
        msg = collate_errors("Error(s) occurred when checking types", errors)
        raise ValidationError(msg)

    return outgoing


def _typenade(
    incoming: JSONDict,
    types: JSONDict,
    *,
    fixate: bool = True,
    address: Tuple[str] = ()
) -> Tuple[JSONDict, List[Error]]:
    """Perform type checking and optionally type fixing.

    Parameters
    ----------
    incoming: JSONDict
        The input `dict`. This is supposed to be the one obtained by merging
        user and template `dict`-s.
    types: JSONDict
        Types of all keywords in the input. Generated from :func:`view_by_types`.
    fixate: bool
        Whether to call the type constructor on the value, to fixate its type.
    address: Tuple[str]
        A tuple of keys need to index the current value in the recursion. See
        Notes.

    Returns
    -------
    outgoing: JSONDict
        A dictionary with all default values fixed.
    errors_at: List[Tuple[str]]
        A list of keys to access elements in the `dict` that raised an error.
        See Notes.
    """

    outgoing = {}
    errors = []

    for k, v in incoming.items():
        if isinstance(v, dict):
            outgoing[k], errs = _typenade(
                incoming=v, types=types[k], fixate=fixate, address=(address + (k,))
            )
            errors.extend(errs)
        else:
            declared = types[k]
            if type_matches(incoming[k], declared):
                outgoing[k] = (
                    type_fixers[declared](incoming[k]) if fixate else incoming[k]
                )
            else:
                errors.append(
                    Error(
                        address + (k,),
                        "Actual ({0}) and declared ({1}) types do not match".format(
                            type(incoming[k]).__name__, declared
                        ),
                    )
                )
                outgoing[k] = None

    return outgoing, errors
