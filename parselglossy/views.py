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
"""Tools to extract views of dictionaries."""

from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import SpecificationError
from .utils import JSONDict


def view_by(
    what: str,
    d: Dict[str, Any],
    *,
    predicate: Callable[[Any, str], bool] = lambda x, y: True,
    missing: Union[None, Exception] = None,
    transformer: Callable[[Any], Any] = lambda x: x
) -> JSONDict:
    """Recursive decimation of a template into an input.

    Parameters
    ----------
    what: str
    d: JSONDict
    predicate: Callable
       A predicate accepting one argument.
    missing: Union[None, Exception]
    transformer: Callable

    Notes
    -----
    Why don't we just throw an exception as soon as something goes wrong?
    For example, consider this pattern:

    .. code-block:: python
       view = {v['name']: transformer(v[what]) if all([what in v, predicate(v, what)]) else missing for v in d['keywords']}

    we could just embed in a ``try``-``except`` and catch it. However, we want
    to produce errors that are as informative as possible, hence we decide to
    keep track of what went wrong and raise only when validation is done.
    """

    view = {
        v["name"]: transformer(v[what])
        if all([what in v, predicate(v, what)])
        else missing
        for v in d["keywords"]
    }

    if "sections" in d:
        for section in d["sections"]:
            view[section["name"]] = view_by(
                what,
                section,
                predicate=predicate,
                missing=missing,
                transformer=transformer,
            )

    return view


def apply_mask(incoming: JSONDict, mask: Dict[str, Callable[[Any], Any]]) -> JSONDict:
    """Apply a mask over a dictionary.

    Parameters
    ----------
    incoming: JSONDict
        Dictionary to be masked.
    mask: Dict[str, Callable[[Any], Any]]
        Mask to apply to `incoming`.

    Notes
    -----
    There are no checks on consistency of the structure of the two dictionaries.
    """

    outgoing = {}
    for k, v in incoming.items():
        if isinstance(v, dict):
            outgoing[k] = apply_mask(v, mask[k])
        elif v is None:
            outgoing[k] = None
        else:
            outgoing[k] = mask[k](v)

    return outgoing


def predicate_checker(incoming: Dict[str, Optional[List[str]]]) -> JSONDict:
    """Check that predicates are valid Python.

    Parameters
    ----------

    Returns
    -------
    """
    outgoing = {}
    for k, ps in incoming.items():
        if isinstance(ps, dict):
            outgoing[k] = predicate_checker(ps)
        elif ps is None:
            outgoing[k] = None
        else:
            outgoing[k] = []
            for p in ps:
                try:
                    outgoing[k].append(compile(p, "<unknown>", "eval"))
                except SyntaxError:
                    outgoing[k].append(
                        SpecificationError(
                            'Python syntax error in predicate "{:s}"'.format(p)
                        )
                    )

    return outgoing
