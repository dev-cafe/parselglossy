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

"""Facilities for checking input templates"""

import re
from copy import deepcopy
from typing import Tuple, List, Any

import networkx as nx

from .exceptions import Error, ParselglossyError, collate_errors
from .utils import JSONDict, location_in_dict
from .types import allowed_types
from .views import view_by_default, view_by_default_keywords


def is_template_valid(template: JSONDict) -> JSONDict:
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

    * Reorders keywords according to their dependencies.

    Parameters
    ----------
    template : JSONDict

    Returns
    -------
    ordered : JSONDict

    Raises
    ------
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over the recursive :func:`_rec_is_template_valid`.
    """

    errors = _rec_is_template_valid(template)
    errors.extend(_check_cyclic_defaults(template))

    if errors:
        msg = collate_errors(when="checking the template", errors=errors)
        raise ParselglossyError(msg)

    return _reorder_template(template)


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
        errs = _check_keyword(k, address=address)
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


def _check_keyword(keyword: JSONDict, *, address: Tuple = ()) -> List[Error]:
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


def _undocumented(x: JSONDict) -> bool:
    return (
        True if "docstring" not in x.keys() or x["docstring"].strip() == "" else False
    )


def _untyped(x: JSONDict) -> bool:
    return True if "type" not in x.keys() or x["type"] not in allowed_types else False
