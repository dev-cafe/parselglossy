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

from typing import Optional

from .exceptions import ParselglossyError, collate_errors
from .utils import JSONDict
from .validation_plumbing import (
    rec_check_predicates,
    rec_fix_defaults,
    rec_is_template_valid,
    rec_merge_ours,
    rec_typenade,
)


def is_template_valid(template: JSONDict) -> Optional[bool]:
    """Checks a template `dict` is well-formed.

    Parameters
    ----------
    template : JSONDict

    Returns
    -------
    is_valid : Optional[bool]

    Raises
    ------
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over the recursive :func:`rec_is_template_valid`.
    """

    is_valid = True
    errors = rec_is_template_valid(template)

    if errors:
        is_valid = False
        msg = collate_errors(when="checking the template", errors=errors)
        raise ParselglossyError(msg)

    return is_valid


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


def fix_defaults(incoming: JSONDict, *, types: JSONDict) -> Optional[JSONDict]:
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

    outgoing, errors = rec_fix_defaults(incoming, types=types)

    if errors:
        msg = collate_errors(when="fixing defaults", errors=errors)
        raise ParselglossyError(msg)

    return outgoing


def typenade(incoming: JSONDict, types: JSONDict) -> Optional[JSONDict]:
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
    This is porcelain over the recursive function :func:`rec_typenade`.
    """
    outgoing, errors = rec_typenade(incoming, types)

    if errors:
        msg = collate_errors(when="checking types", errors=errors)
        raise ParselglossyError(msg)

    return outgoing


def check_predicates(incoming: JSONDict, *, predicates: JSONDict) -> Optional[JSONDict]:
    """Run predicates on input tree with fixed defaults.

    Parameters
    ----------
    incoming : JSONDict
        The input `dict`. This is supposed to be the result of :func:`fix_defaults`.
    predicates : JSONDict
        A view-by-predicates of the template ``dict``.

    Returns
    -------
    outgoing : JSONDict
        A dictionary with all values checked.

    Raises
    ------
    :exc:`ParselglossyError`

    Notes
    -----
    This is porcelain over recursive function :func:`rec_check_predicates`.
    """

    outgoing, errors = rec_check_predicates(incoming, predicates=predicates)

    if errors:
        msg = collate_errors(when="checking predicates", errors=errors)
        raise ParselglossyError(msg)

    return outgoing
