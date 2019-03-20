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

from typing import List, Optional, Tuple

from .exceptions import Error, ParselglossyError, collate_errors
from .types import allowed_types
from .utils import JSONDict, check_callable


def check_template(template: JSONDict) -> Optional[JSONDict]:
    """Checks a template `dict` is well-formed.

    Parameters
    ----------
    template : JSONDict

    Returns
    -------
    outgoing : Optional[JSONDict]

    Raises
    ------
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over the recursive :func:`rec_check_template`.
    """

    outgoing, errors = rec_check_template(template)

    if errors:
        msg = collate_errors(when="checking the template", errors=errors)
        raise ParselglossyError(msg)

    return outgoing


def undocumented(x: JSONDict) -> bool:
    return (
        True if "docstring" not in x.keys() or x["docstring"].strip() == "" else False
    )


def untyped(x: JSONDict) -> bool:
    return True if "type" not in x.keys() or x["type"] not in allowed_types else False


def check_keyword(
    keyword: JSONDict, *, address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
    """Checks that a template keyword is well-formed.

    In this function, a template keyword is well-formed if it has:

    * An allowed type.
    * A non-empty docstring.

    The two additional criteria:

    * A default callable that is valid Python, if present.
    * Predicates that are valid Python, if present.

    can only be checked meaningfully later, as they might depend on
    keyword(s)/section(s) of the input that are only known after merging.

    Parameters
    ----------
    template : JSONDict
    address : Tuple

    Returns
    -------
    outgoing : JSONDict
    errors : List[Error]
    """

    outgoing = {}
    errors = []

    k = keyword["name"]
    if "sections" in keyword.keys():
        errors.append(
            Error((address + (k,)), "Sections cannot be nested under keywords.")
        )
    else:
        outgoing = keyword

    if untyped(keyword):
        errors.append(Error((address + (k,)), "Keywords must have a valid type."))
    else:
        outgoing = keyword

    if undocumented(keyword):
        errors.append(
            Error((address + (k,)), "Keywords must have a non-empty docstring.")
        )
    else:
        outgoing = keyword

    # if "predicates" in keyword.keys():
    #    for p in keyword["predicates"]:
    #        # Replace convenience placeholder value with its full "address"
    #        where = location_in_dict(address=(address + (k,)))
    #        p = sub("value", where, p)
    #        invalid, msg = is_callable_valid(p, start_dict)
    #        if invalid:
    #            errors.append(Error((address + (k,)), msg))
    # else:
    #    outgoing = keyword

    return outgoing, errors


def rec_check_template(
    template: JSONDict, *, address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
    """Checks a template `dict` is well-formed.

    A template `dict` is well-formed if:

    * All keywords have:

      - An allowed type.
      - A non-empty docstring.
      - A default callable that is valid Python, if present.
      - Predicates that are valid Python, if present.

      Note that the latter two criteria can only be checked later on.

    * No sections are nested under keywords.

    * All sections have a non-empty docstring.

    Parameters
    ----------
    template : JSONDict
    address : Tuple[str]

    Returns
    -------
    outgoing : JSONDict
    errors : List[Error]
    """

    outgoing = {}
    errors = []

    keywords = template["keywords"] if "keywords" in template.keys() else []
    for k in keywords:
        out, errs = check_keyword(k, address=address)
        outgoing["keywords"] = [out]
        errors.extend(errs)

    sections = template["sections"] if "sections" in template.keys() else []
    for s in sections:
        if undocumented(s):
            errors.append(
                Error(
                    (address + (s["name"],)),
                    "Sections must have a non-empty docstring.",
                )
            )
            outgoing["sections"] = [None]
        out, errs = rec_check_template(s, address=(address + (s["name"],)))
        outgoing["sections"] = [out]
        errors.extend(errs)

    return outgoing, errors


def merge_ours(*, theirs: JSONDict, ours: JSONDict) -> Optional[JSONDict]:
    """Recursively merge two `dict`-s with "ours" strategy.

    Parameters
    ----------
    theirs : JSONDict
    ours : JSONDict

    Returns
    -------
    outgoing : JSONDict

    Raises
    ------
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over the recursive function :func:`rec_merge_ours`.
    """
    outgoing, errors = rec_merge_ours(theirs=theirs, ours=ours)

    if errors:
        msg = collate_errors(when="merging", errors=errors)
        raise ParselglossyError(msg)

    return outgoing


def rec_merge_ours(*, theirs: JSONDict, ours: JSONDict) -> Tuple[JSONDict, List[Error]]:
    """Recursively merge two `dict`-s with "ours" strategy.

    Parameters
    ----------
    theirs : JSONDict
    ours : JSONDict

    Returns
    -------
    outgoing : JSONDict

    Notes
    -----
    The `theirs` dictionary is supposed to be the view by defaults of the
    validation specification, whereas `ours` is the dictionary from user input.
    The recursive merge action will generate a complete, but not validated,
    input dictionary by using default values where these are not overridden by
    user input, hence the naming "ours" for the merge strategy.
    """
    outgoing = {}
    errors = []

    # Check whether ours has keywords/sections that are unknown
    difference = set(ours.keys()).difference(set(theirs.keys()))
    if difference != set():
        for k in difference:
            what = "section" if isinstance(ours[k], dict) else "keyword"
            errors.append(Error(message="Found unexpected {}: '{}'".format(what, k)))

    for k, v in theirs.items():
        if k not in ours.keys():
            outgoing[k] = theirs[k]
        elif isinstance(v, dict):
            outgoing[k], errs = rec_merge_ours(theirs=v, ours=ours[k])
            errors.extend(errs)
        else:
            outgoing[k] = ours[k]

    return outgoing, errors


def fix_defaults(incoming: JSONDict) -> Optional[JSONDict]:
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
    This is porcelain over recursive function :func:`rec_fix_defaults`.
    """

    outgoing, errors = rec_fix_defaults(incoming)

    if errors:
        msg = collate_errors(when="fixing defaults", errors=errors)
        raise ParselglossyError(msg)

    return outgoing


def rec_fix_defaults(
    incoming: JSONDict, *, start_dict: JSONDict = None, address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
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
    errors_at: List[Error]
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
        if isinstance(v, dict):
            outgoing[k], errs = rec_fix_defaults(
                incoming=v, start_dict=start_dict, address=(address + (k,))
            )
            errors.extend(errs)
        elif v is None:
            outgoing[k] = None  # type: ignore
        else:
            msg, outgoing[k] = check_callable(v, start_dict)
            if msg != "":
                errors.append(Error((address + (k,)), msg))

    return outgoing, errors
