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
"""Validation facilities."""

from typing import List, Tuple

from .exceptions import Error, SpecificationError, collate_errors
from .utils import JSONDict


def merge_ours(*, theirs: JSONDict, ours: JSONDict) -> JSONDict:
    """Recursively merge two `dict`-s with "ours" strategy.

    Parameters
    ----------
    theirs: JSONDict
    ours: JSONDict

    Returns
    -------
    outgoing: JSONDict

    Notes
    -----
    The `theirs` dictionary is supposed to be the view by defaults of the
    validation specification, whereas `ours` is the dictionary from user input.
    The recursive merge action will generate a complete, but not validated,
    input dictionary by using default values where these are not overridden by
    user input, hence the naming "ours" for the merge strategy.
    """
    outgoing = {}

    for k, v in theirs.items():
        if isinstance(v, dict):
            outgoing[k] = merge_ours(theirs=v, ours=ours[k])
        elif k not in ours.keys():
            outgoing[k] = theirs[k]
        else:
            outgoing[k] = ours[k]

    return outgoing


def fix_defaults(incoming: JSONDict) -> JSONDict:
    """Fixes defaults from a merge input ``dict``.

    Parameters
    ----------
    incoming: JSONDict
        The input `dict`. This is supposed to be the one obtained by merging
        user and template `dict`-s.

    Returns
    -------
    outgoing: JSONDict
        A dictionary with all default values fixed.

    Raises
    ------
    :exc:`SpecificationError`

    Notes
    -----
    This is porcelain over :func:`_fix_defaults`.
    """

    outgoing, errors = _fix_defaults(incoming)

    if errors:
        msg = collate_errors(errors)
        raise SpecificationError(msg)

    return outgoing


def _fix_defaults(
    incoming: JSONDict, *, start_dict: JSONDict = None, address: Tuple[str] = ()
) -> Tuple[JSONDict, List[Tuple[str]]]:
    """Fixes default values from a merge input ``dict``.

    Parameters
    ----------
    incoming: JSONDict
        The input `dict`. This is supposed to be the one obtained by merging
        user and template `dict`-s.
    start_dict: JSONDict
        The `dict` we start recursion from. See Notes.
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

    Notes
    -----
    Since we allow callable actions to appear as defaults, we need to run them
    to determine the actual default values.
    This *must* be done **before** type checking and fixation, otherwise we end
    up with false negatives or ambiguous type checks. For example:

    * If the type is ``str`` and the default a callable action, the type will
      match, but the default will make no sense.
    * If the type is numerical, *e.g.* ``int``, the type will not match.

    To overcome these ambiguities, we decide to turn all default fields into
    lambda functions. These are first compiled, to ensure that the syntax of
    callable actions is correct, and then executed::

        # Transform to a string
        a = 'lambda x: {:s}'.format(incoming[k])
        # Evaluate, within a ``try``-``except`` block, and set defaults
        outgoing[k] = eval(a)(start_dict)

    We need to pass the full ``incoming`` dictionary as argument to the
    ``eval``, because we allow indexing in the *global* ``dict``. That is,
    since it is **allowed** to define defaults in a given section based on
    defaults in other section we **must** be able to access the full input at
    any point. The ``start_dict`` parameter allows us to do this.

    Rather than throw errors, we keep track of where the execution of a
    callable failed and why in the ``errors_at`` return variable. This is a
    list of addressing tuples.
    """

    outgoing = {}
    errors = []

    if start_dict is None:
        start_dict = incoming

    for k, v in incoming.items():
        address += (k,)
        if isinstance(v, dict):
            outgoing[k], errs = _fix_defaults(
                incoming=v, start_dict=start_dict, address=address
            )
            errors.extend(errs)
        elif v is None:
            outgoing[k] = None
        else:
            # Transform field into lambda function and evaluate it
            # This might throw SyntaxError, TypeError or KeyError
            try:
                # FIXME How robust is this string manipulation? Might we
                # fudge it up with truncation?
                outgoing[k] = eval("lambda user: ({})".format(v))(start_dict)
            except KeyError as e:
                errors.append(
                    Error(
                        address, "KeyError {} in defaulting closure '{:s}'".format(e, v)
                    )
                )
                outgoing[k] = None
            except SyntaxError as e:
                errors.append(
                    Error(
                        address,
                        "SyntaxError {} in defaulting closure '{:s}'".format(e, v),
                    )
                )
                outgoing[k] = None
            except TypeError as e:
                errors.append(
                    Error(
                        address,
                        "TypeError {} in defaulting closure '{:s}'".format(e, v),
                    )
                )
                outgoing[k] = None

    return outgoing, errors


type_fix_callbacks = {
    "bool": bool,
    # We remove spaces so the string-to-complex cast works without surprises
    "complex": lambda x: complex(x.replace(" ", "")),
    "float": float,
    "int": int,
    "str": str,
}
tmp = {
    "List[{:s}]".format(k): lambda x: list(map(v, x))
    for k, v in type_fix_callbacks.items()
}
type_fix_callbacks.update(tmp)
"""Dict[str, Callable[[Any], Any]: dictionary holding function for type fixation.

The `complex` type constructor from `str` only works when there are no spaces
between real and imaginary parts.
"""


# FIXME This function does not yet do what it purports to
def typenade(incoming: JSONDict, *, fixate: bool = False) -> JSONDict:
    """Perform type checking  and optionally type fixing.

    Parameters
    ----------
    incoming: JSONDict
    fixate: bool
        Whether to fix types.

    Returns
    -------
    outgoing: JSONDict

    Notes
    -----
    If type checking fails, we store a :py:exc:`ValidationError` as value in the
    `outgoing` dictionary. This allows reporting errors globally later on.
    """

    outgoing = {}

    for k, v in incoming.items():
        if isinstance(v, dict):
            outgoing[k] = typenade(incoming=v, fixate=fixate)
        else:
            outgoing[k] = incoming[k]

    return outgoing
