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
    """Fix default value and perform type checking.

    Parameters
    ----------
    incoming : JSONDict
        The input ``dict``. This is supposed to be the one obtained by merging
        user and template ``dict``-s.
    types: JSONDict
        Types of all keywords in the input. Generated from :func:`view_by_types`.
    start_dict : JSONDict
        The ``dict`` we start recursion from. This parameter is needed to keep
        around a copy of the full ``dict`` during the recursion.
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

    This operation must be done with some care, to avoid false negatives or
    ambiguous type checks. For example:

    * If the type is ``str`` and the default a callable, the type will
      match, but the default will make no sense.
    * If the type is numerical, *e.g.* ``int``, the type will not match.

    However, by design the callables **must** refer to some other field in the
    input tree, hence they **must** contain the reserved token "user". This
    allows us to disambiguate a callable as default from a value as default.

    The final strategy adopted is then:

    1. Perform type checking with :func:`type_matches`. If successful, we
    coerce the type.
    2. If types did not match, we further check whether the value is a string,
    containing the reserved token "value". This means the default value is
    actually a callable. We run the callable, which internally coerces the type
    of the result to the expected one.
    3. If even this check was unsuccessful, types really were unmatched. We
    report the error and move on.
    """

    outgoing = {}
    errors = []

    if start_dict is None:
        start_dict = incoming

    for k, v in incoming.items():
        if not isinstance(v, dict):
            t = types[k]
            types_ok = type_matches(v, t)
            if types_ok:
                # Yes! Types match up front, you're awesome
                msg = ""
                outgoing[k] = type_fixers[t](v)
            else:
                # Types did not match :/
                if type(v).__name__ == "str" and "user" in v:
                    # BUT! It's actually a string and it's a callable
                    # We assume that if it contains the reserved tokens "value"
                    # or "user" we're trying to perform some sort of defaulting
                    # action.
                    msg, outgoing[k] = run_callable(v, start_dict, t=t)
                else:
                    # NOPE. You're an unrepentant sinner
                    actual = (
                        type(v).__name__
                        if type(v) is not list
                        else "List[{}]".format(", ".join([type(x).__name__ for x in v]))
                    )
                    msg = "Actual ({0}) and declared ({1}) types do not match.".format(
                        actual, t
                    )
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


def rec_check_predicates(
    incoming: JSONDict,
    *,
    predicates: JSONDict,
    start_dict: JSONDict = None,
    address: Tuple = ()
) -> List[Error]:
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
    errors : List[Error]
        A list of keys to access elements in the `dict` that raised an error.
    """

    errors = []

    if start_dict is None:
        start_dict = incoming

    for k, v in incoming.items():
        if predicates[k] is not None:
            if not isinstance(v, dict):
                for p in predicates[k]:
                    where = location_in_dict(address=(address + (k,)))
                    msg, success = run_predicate(p, where, start_dict)
                    if not success:
                        errors.append(Error((address + (k,)), msg))
            else:
                errs = rec_check_predicates(
                    incoming=v,
                    predicates=predicates[k],
                    start_dict=start_dict,
                    address=(address + (k,)),
                )
                errors.extend(errs)

    return errors


def run_predicate(predicate: str, where: str, user: JSONDict) -> Tuple[str, bool]:
    """Run a predicate to check whether it is satisfied.

    Parameters
    ----------
    predicate : str
    where : str
    user : JSONDict

    Returns
    -------

    Notes
    -----
    We replace the convenience placeholder "value" with its full "address" in ``user``.
    """

    p = predicate.replace("value", where)
    postfix = "in closure '{}'.".format(predicate)

    try:
        msg = ""
        success = eval("lambda user: {}".format(p))(user)
        if not success:
            msg = "Predicate '{}' not satisfied.".format(predicate)
    except KeyError as e:
        msg = "KeyError {} {:s}".format(e, postfix)
        success = False
    except SyntaxError as e:
        msg = "SyntaxError {} {:s}".format(e, postfix)
        success = False
    except TypeError as e:
        msg = "TypeError {} {:s}".format(e, postfix)
        success = False
    except NameError as e:
        msg = "NameError {} {:s}".format(e, postfix)
        success = False

    return msg, success


def run_callable(f: str, d: JSONDict, *, t: str) -> Tuple[str, Optional[Any]]:
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

    Returns
    -------
    retval : Tuple[str, Optional[Any]]
        The error message, if any, and the result of the callable, if any.

    Notes
    -----
    The input tree is called ``user``.
    The callable is turned into a lambda function and executed using ``eval``,
    to ensure that the syntax of callable actions is correct and that the
    callable returns correctly.

    We need to pass the full ``incoming`` dictionary as argument to
    ``eval``, because we allow indexing in the *global* ``dict``. That is,
    since it is **allowed** to define defaults in a given section based on
    defaults in other section we **must** be able to access the full input at
    any point.
    """

    closure = "lambda user: {}"
    postfix = "in closure '{}'.".format(f)

    try:
        msg = ""
        result = eval(closure.format(f))(d)
        result = type_fixers[t](result)
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
