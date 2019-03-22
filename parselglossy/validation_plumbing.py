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
"""Plumbing functions powering our validation facilities."""

from typing import Any, List, Optional, Tuple

from .exceptions import Error
from .types import allowed_types, type_fixers, type_matches
from .utils import JSONDict, location_in_dict


def undocumented(x: JSONDict) -> bool:
    return (
        True if "docstring" not in x.keys() or x["docstring"].strip() == "" else False
    )


def untyped(x: JSONDict) -> bool:
    return True if "type" not in x.keys() or x["type"] not in allowed_types else False


def check_keyword(keyword: JSONDict, *, address: Tuple = ()) -> List[Error]:
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
    errors : List[Error]
    """

    errors = []

    k = keyword["name"]
    if "sections" in keyword.keys():
        errors.append(
            Error((address + (k,)), "Sections cannot be nested under keywords.")
        )

    if untyped(keyword):
        errors.append(Error((address + (k,)), "Keywords must have a valid type."))

    if undocumented(keyword):
        errors.append(
            Error((address + (k,)), "Keywords must have a non-empty docstring.")
        )

    return errors


def rec_is_template_valid(template: JSONDict, *, address: Tuple = ()) -> List[Error]:
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
    errors : List[Error]
    """

    errors = []

    keywords = template["keywords"] if "keywords" in template.keys() else []
    for k in keywords:
        errs = check_keyword(k, address=address)
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
        errs = rec_is_template_valid(s, address=(address + (s["name"],)))
        errors.extend(errs)

    return errors


def rec_merge_ours(
    *, theirs: JSONDict, ours: JSONDict, address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
    """Recursively merge two `dict`-s with "ours" strategy.

    Parameters
    ----------
    theirs : JSONDict
    ours : JSONDict
    address : Tuple

    Returns
    -------
    outgoing : JSONDict
    errors : List[Error]

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
            errors.append(Error(message="Found unexpected {}: '{}'.".format(what, k)))

    for k, v in theirs.items():
        if k not in ours.keys():
            if theirs[k] is not None:
                outgoing[k] = theirs[k]
            else:
                outgoing[k] = None
                msg = "Keyword '{0}' is required but has no value.".format(k)
                errors.append(Error((address + (k,)), msg))
        elif not isinstance(v, dict):
            outgoing[k] = ours[k]
        else:
            outgoing[k], errs = rec_merge_ours(
                theirs=v, ours=ours[k], address=(address + (k,))
            )
            errors.extend(errs)

    return outgoing, errors


def rec_fix_defaults(
    incoming: JSONDict,
    *,
    types: JSONDict,
    start_dict: JSONDict = None,
    address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
    """Fixes default values from a merge input ``dict``.

    Parameters
    ----------
    incoming : JSONDict
        The input `dict`. This is supposed to be the one obtained by merging
        user and template `dict`-s.
    start_dict : JSONDict
        The `dict` we start recursion from. See Notes.
    address : Tuple[str]
        A tuple of keys need to index the current value in the recursion. See
        Notes.

    Returns
    -------
    outgoing : JSONDict
        A dictionary with all default values fixed.
    errors : List[Error]
        A list of keys to access elements in the `dict` that raised an error.
        See Notes.

    Notes
    -----
    Since we allow callables to appear as defaults, we need to run them
    to determine the actual default values.
    This *must* be done **before** type checking and fixation, otherwise we end
    up with false negatives or ambiguous type checks. For example:

    * If the type is ``str`` and the default a callable, the type will
      match, but the default will make no sense.
    * If the type is numerical, *e.g.* ``int``, the type will not match.

    To overcome these ambiguities, we decide to turn all default fields into
    lambda functions. These are executed using ``eval``, to ensure that the
    syntax of callable actions is correct and that the callable returns
    correctly::

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
    callable failed and why in the ``errors`` return variable. This is a
    list of addressing tuples.
    """

    outgoing = {}
    errors = []

    if start_dict is None:
        start_dict = incoming

    for k, v in incoming.items():
        if not isinstance(v, dict):
            msg, outgoing[k] = run_callable(v, start_dict, t=types[k])
            if msg != "":
                errors.append(Error(address + (k,), msg))
        else:
            outgoing[k], errs = rec_fix_defaults(
                incoming=v,
                types=types[k],
                start_dict=start_dict,
                address=(address + (k,)),
            )
            errors.extend(errs)

    return outgoing, errors


def rec_typenade(
    incoming: JSONDict, types: JSONDict, *, address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
    """Perform type checking and type fixing.

    Parameters
    ----------
    incoming: JSONDict
        The input `dict`. This is supposed to be the one obtained by merging
        user and template `dict`-s.
    types: JSONDict
        Types of all keywords in the input. Generated from :func:`view_by_types`.
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
        if not isinstance(v, dict):
            t = types[k]
            if type_matches(incoming[k], t):
                outgoing[k] = type_fixers[t](incoming[k])
            else:
                msg = "Actual ({0}) and declared ({1}) types do not match.".format(
                    type(incoming[k]).__name__, t
                )
                errors.append(Error(address + (k,), msg))
                outgoing[k] = None  # type: ignore
        else:
            outgoing[k], errs = rec_typenade(
                incoming=v, types=types[k], address=(address + (k,))
            )
            errors.extend(errs)

    return outgoing, errors


def rec_check_predicates(
    incoming: JSONDict,
    *,
    predicates: JSONDict,
    start_dict: JSONDict = None,
    address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
    """Run predicates on input tree with fixed defaults.

    Parameters
    ----------
    incoming : JSONDict
        The input `dict`. This is supposed to be the result of :func:`fix_defaults`.
    predicates : JSONDict
        A view-by-predicates of the template ``dict``.
    start_dict : JSONDict
        The `dict` we start recursion from.
    address : Tuple[str]
        A tuple of keys need to index the current value in the recursion.

    Returns
    -------
    outgoing : JSONDict
        A dictionary with all default values fixed.
    errors : List[Error]
        A list of keys to access elements in the `dict` that raised an error.
    """

    outgoing = {}
    errors = []

    if start_dict is None:
        start_dict = incoming

    for k, v in incoming.items():
        if predicates[k] is not None:
            if not isinstance(v, dict):
                for p in predicates[k]:
                    # Replace convenience placeholder "value" with its full "address"
                    where = location_in_dict(address=(address + (k,)))
                    msg, success = run_callable(p.replace("value", where), start_dict)
                    if success:
                        outgoing[k] = v
                    else:
                        errors.append(Error((address + (k,)), msg))
            else:
                outgoing[k], errs = rec_check_predicates(
                    incoming=v,
                    predicates=predicates[k],
                    start_dict=start_dict,
                    address=(address + (k,)),
                )
                errors.extend(errs)
        else:
            outgoing[k] = v

    return outgoing, errors


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
