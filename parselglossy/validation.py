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

import json
from pathlib import Path
from typing import Union

from .exceptions import ParselglossyError, collate_errors
from .utils import ComplexEncoder, JSONDict, path_resolver
from .validation_plumbing import (
    rec_check_predicates,
    rec_fix_defaults,
    rec_is_template_valid,
    rec_merge_ours,
)
from .views import view_by_default, view_by_predicates, view_by_type


def validate_from_dicts(
    *, ir: JSONDict, template: JSONDict, fr_file: Union[str, Path] = None
) -> JSONDict:
    """Validate intermediate representation into final representation.

    Parameters
    ----------
    dumpir : bool
        Whether to serialize FR to JSON. Location and name of file are
        determined based on the input file.
    ir : JSONDict
        Intermediate representation of the input file.
    fr_file : Union[str, Path]
         File to write final representation to (JSON format).
         None by default, which means file is not written out.

    Returns
    -------
    fr : JSONDict
        The validated input.

    Raises
    ------
    :exc:`ParselglossyError`
    """
    is_template_valid(template)
    stencil = view_by_default(template)
    types = view_by_type(template)
    predicates = view_by_predicates(template)

    fr = merge_ours(theirs=stencil, ours=ir)
    fr = fix_defaults(fr, types=types)
    check_predicates(fr, predicates=predicates)

    if fr_file is not None:
        fr_file = path_resolver(fr_file)
        with fr_file.open("w") as out:
            json.dump(fr, out, cls=ComplexEncoder, indent=4)

    return fr


def is_template_valid(template: JSONDict) -> None:
    """Checks a template `dict` is well-formed.

    Parameters
    ----------
    template : JSONDict

    Raises
    ------
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over the recursive :func:`rec_is_template_valid`.
    """

    errors = rec_is_template_valid(template)

    if errors:
        msg = collate_errors(when="checking the template", errors=errors)
        raise ParselglossyError(msg)


def merge_ours(*, theirs: JSONDict, ours: JSONDict) -> JSONDict:
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


def fix_defaults(incoming: JSONDict, *, types: JSONDict) -> JSONDict:
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
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over recursive function :func:`rec_fix_defaults`.
    """

    outgoing, errors = rec_fix_defaults(incoming, types=types)

    if errors:
        msg = collate_errors(when="fixing defaults", errors=errors)
        raise ParselglossyError(msg)

    return outgoing


def check_predicates(incoming: JSONDict, *, predicates: JSONDict) -> None:
    """Run predicates on input tree with fixed defaults.

    Parameters
    ----------
    incoming : JSONDict
        The input `dict`. This is supposed to be the result of :func:`fix_defaults`.
    predicates : JSONDict
        A view-by-predicates of the template ``dict``.

    Raises
    ------
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over recursive function :func:`rec_check_predicates`.
    """

    errors = rec_check_predicates(incoming, predicates=predicates)

    if errors:
        msg = collate_errors(when="checking predicates", errors=errors)
        raise ParselglossyError(msg)
