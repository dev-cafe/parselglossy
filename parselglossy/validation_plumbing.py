# -*- coding: utf-8 -*-
#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2020 Roberto Di Remigio, Radovan Bast, and contributors.
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

"""Plumbing functions powering our validation facilities."""

import re
from copy import deepcopy
from typing import Any, List, Optional, Tuple

import networkx as nx

from .exceptions import Error
from .types import allowed_types, type_fixers, type_matches
from .utils import JSONDict, location_in_dict, nested_set
from .views import view_by_default, view_by_default_keywords


def _rec_is_template_valid(template: JSONDict, *, address: Tuple = ()) -> List[Error]:
    """Checks a template ``dict`` is well-formed.

    A template ``dict`` is well-formed if:

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
        if _undocumented(s):
            errors.append(
                Error(
                    (address + (s["name"],)),
                    "Sections must have a non-empty docstring.",
                )
            )
        errs = _rec_is_template_valid(s, address=(address + (s["name"],)))
        errors.extend(errs)

    return errors


def _check_cyclic_defaults(template: JSONDict) -> List[Error]:
    """Check for cyclic dependencies between defaulting actions."""
    stencil = view_by_default(template)
    dependencies = _sections_default_dependencies(stencil)
    # for nx we need to translate from tuples of lists to tuples of tuples
    dependencies_hashable = [
        (tuple(_from), tuple(_to)) for (_from, _to) in dependencies
    ]
    G = nx.DiGraph(dependencies_hashable)
    cycles = nx.simple_cycles(G)
    errors = []
    for c in cycles:
        errors.append(
            Error(
                c[0],
                f"Keyword depends cyclically on keyword {location_in_dict(address=c[1])}",  # noqa: E501
            )
        )
    return errors


def _sections_default_dependencies(
    section: JSONDict, parent_sections: List[str] = []
) -> List[Any]:
    """Collects a list of of tuples (keyword, default dependency).

    Both the keyword and the default dependency are lists.

    One such a tuple could look like this:
    (['main section', 'subsection', 'keyword'], ['main section', 'another keyword'])
    """
    dependencies = []
    for k, v in section.items():
        if not isinstance(v, dict):
            dependencies += _keywords_default_dependencies(k, v, parent_sections)
        else:
            dependencies += _sections_default_dependencies(v, parent_sections + [k])
    return dependencies


def _keywords_default_dependencies(
    keyword: str, default: str, parent_sections: List[str]
) -> List[Any]:
    """Collects a list of of tuples (keyword, default dependency) within one section.

    Both the keyword and the default dependency are lists.

    One such a tuple could look like this:
    (['main section', 'subsection', 'keyword'], ['main section', 'another keyword'])
    """
    dependencies = []
    if isinstance(default, str) and "user" in default:
        _to = re.findall(r'\[[\'"](.*?)[\'"]\]', default)
        if len(_to) > 0:
            _from = parent_sections + [keyword]
            dependencies.append((_from, _to))
    return dependencies


def _reorder_template(template: JSONDict) -> JSONDict:
    """Reorder template according to direct graph of keyword dependencies

    Parameters
    ----------
    template : JSONDict

    Returns
    -------
    ordered : JSONDict

    Notes
    -----
    This function reorders the template in place.

    Warnings
    --------
    We are assuming that there are no dependency cycles in the template. Call
    this function **after** :func:`_check_cyclic_defaults`.
    """

    ordered = deepcopy(template)
    _rec_reoder_template(ordered)
    return ordered


def _rec_reoder_template(template: JSONDict) -> None:
    """Recursive backend for :func:`_reorder_template`.

    Parameters
    ----------
    template : JSONDict
    """
    keywords = template["keywords"] if "keywords" in template.keys() else []
    kw_stencil = view_by_default_keywords(keywords)
    deps = _sections_default_dependencies(kw_stencil)
    deps_hashable = [(tuple(_from), tuple(_to)) for (_from, _to) in deps]
    nodes = reversed([x[-1] for x in nx.DiGraph(deps_hashable)])

    shuffle = []
    for node in nodes:
        for x in keywords:
            if x["name"] == node:
                shuffle.append(deepcopy(x))
                keywords.remove(x)
    keywords.extend(shuffle)

    sections = template["sections"] if "sections" in template.keys() else []
    for s in sections:
        _rec_reoder_template(s)


def _rec_merge_ours(
    *, theirs: JSONDict, ours: JSONDict, address: Tuple = ()
) -> Tuple[JSONDict, List[Error]]:
    """Recursively merge two ``dict``-s with "ours" strategy.

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
    The ``theirs`` dictionary is supposed to be the view by defaults of the
    validation specification, whereas ``ours`` is the dictionary from user
    input. The recursive merge action will generate a complete, but not
    validated, input dictionary by using default values where these are not
    overridden by user input, hence the naming "ours" for the merge strategy.
    """
    outgoing = {}
    errors = []

    # Check whether ours has keywords/sections that are unknown
    difference = set(ours.keys()).difference(set(theirs.keys()))
    if difference != set():
        for k in difference:
            what = "section" if isinstance(ours[k], dict) else "keyword"
            errors.append(Error(message=f"Found unexpected {what}: '{k}'."))

    for k, v in theirs.items():
        if k not in ours.keys():
            if theirs[k] is not None:
                outgoing[k] = theirs[k]
            else:
                outgoing[k] = None
                msg = f"Keyword '{k}' is required but has no value."
                errors.append(Error((address + (k,)), msg))
        elif not isinstance(v, dict):
            outgoing[k] = ours[k]
        else:
            outgoing[k], errs = _rec_merge_ours(
                theirs=v, ours=ours[k], address=(address + (k,))
            )
            errors.extend(errs)

    return outgoing, errors


def _rec_fix_defaults(
    incoming: JSONDict,
    *,
    types: JSONDict,
    start_dict: JSONDict = None,
    address: Tuple = (),
) -> Tuple[JSONDict, List[Error]]:
    """Fix default values and perform type checking.

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

    if start_dict is None:
        start_dict = deepcopy(incoming)

    outgoing = {}
    errors = []

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
                if isinstance(v, str) and "user" in v:
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
                        else f"List[{', '.join([type(x).__name__ for x in v])}]"
                    )
                    msg = f"Actual ({actual}) and declared ({t}) types do not match."
            if msg != "":
                errors.append(Error(address + (k,), msg))
            else:
                # Update start_dict.
                # This is so that multiple dependent defaults ("chains") behave
                # correctly. See #76 on GitHub
                nested_set(start_dict, address + (k,), outgoing[k])
        else:
            outgoing[k], errs = _rec_fix_defaults(
                incoming=v,
                types=types[k],
                start_dict=start_dict,
                address=(address + (k,)),
            )
            errors.extend(errs)

    return outgoing, errors


def _rec_check_predicates(
    incoming: JSONDict,
    *,
    predicates: JSONDict,
    start_dict: JSONDict = None,
    address: Tuple = (),
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
                errs = _rec_check_predicates(
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

    try:
        msg = ""
        success = eval(f"lambda user: {p}")(user)
        if not success:
            msg = f"Predicate '{predicate}' not satisfied."
    except KeyError as e:
        msg = f"KeyError {e} in closure '{predicate}'."
        success = False
    except SyntaxError as e:
        msg = f"SyntaxError {e} in closure '{predicate}'."
        success = False
    except TypeError as e:
        msg = f"TypeError {e} in closure '{predicate}'."
        success = False
    except NameError as e:
        msg = f"NameError {e} in closure '{predicate}'."
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

    try:
        msg = ""
        result = eval(f"lambda user: {f}")(d)
        result = type_fixers[t](result)
    except KeyError as e:
        msg = f"KeyError {e} in closure '{f}'."
        result = None
    except SyntaxError as e:
        msg = f"SyntaxError {e} in closure '{f}'."
        result = None
    except TypeError as e:
        msg = f"TypeError {e} in closure '{f}'."
        result = None
    except NameError as e:
        msg = f"NameError {e} in closure '{f}'."
        result = None

    return msg, result


def _undocumented(x: JSONDict) -> bool:
    return (
        True if "docstring" not in x.keys() or x["docstring"].strip() == "" else False
    )


def _untyped(x: JSONDict) -> bool:
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

    if _untyped(keyword):
        errors.append(Error((address + (k,)), "Keywords must have a valid type."))

    if _undocumented(keyword):
        errors.append(
            Error((address + (k,)), "Keywords must have a non-empty docstring.")
        )

    return errors
