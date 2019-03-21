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

from typing import List, Optional, Tuple

from .exceptions import Error, ParselglossyError, collate_errors
from .utils import JSONDict, type_fixers, type_matches


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
                msg = "Actual ({0}) and declared ({1}) types do not match".format(
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
