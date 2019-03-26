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
"""Atoms."""

import functools
from typing import Any, List, Union

import pyparsing as pp

from ..utils import falsey, truthy


def to_bool(x):
    defined = False
    if x is None:
        defined = False
    elif x.upper() in falsey:
        defined = False
    elif x.upper() in truthy:
        defined = True
    else:
        defined = False

    return defined


bool_t = functools.reduce(lambda x, y: x ^ y, map(pp.CaselessLiteral, truthy + falsey))
bool_t.setName("bool")
bool_t.setParseAction(lambda token: to_bool(token[0]))

int_t = pp.pyparsing_common.signed_integer

float_t = pp.pyparsing_common.sci_real

quoted_str_t = pp.quotedString.setParseAction(pp.removeQuotes)
unquoted_str_t = pp.Word(pp.alphas + "_", pp.alphanums + "_")
"""An unquoted string starts with alphabetic characters and underscores,
followed by alphanumeric characters and underscores."""

I_unit = functools.reduce(
    lambda x, y: x ^ y, map(pp.CaselessLiteral, ["*j", "*i"])
).suppress()
complex_t = pp.OneOrMore(pp.pyparsing_common.number) + I_unit
complex_t.setParseAction(
    lambda token: complex(token[0], token[1])
    if len(token) == 2
    else complex(0.0, token[0])
)

num_t = complex_t | float_t | int_t
num_t.setName("numeric")

SDATA = pp.Literal("$").suppress()
EDATA = pp.CaselessLiteral("$end").suppress()
data_t = pp.Group(
    pp.Combine(SDATA + pp.Word(pp.alphas + "_<>", pp.alphanums + "_<>"))
    + pp.SkipTo(EDATA)
    + EDATA
)

fortranStyleComment = pp.Regex(r"!.*").setName("Fortran style comment")


def make_list_t(
    scalars: Union[Any, List[Any]],
    *,
    start: str = "[",
    end: str = "]",
    delimiter: str = ",",
    throw_if_empty: bool = True,
    multiline: bool = True
) -> Any:
    """Atom for lists.

    Parameters
    ----------
    scalars: Union[Any, List[Any]]
        Scalar parser elements, already combined or as a list. The list will be
        combined using the `^` operator.
    start: str
        Left delimiter for the list. Defaults to '['.
    end: str
        Right delimiter for the list. Defaults to ']'.
    delimiter: str
        List delimiter. Defaults to ','.
    multiline: bool
        Whether the list can span multiple lines. Defaults to `True`.

    Notes
    -----
    The order of the scalar tokens in the `scalars` list **is important**.

    Returns
    -------
    list: Any
    """
    START, END = map(pp.Suppress, start + end)

    if isinstance(scalars, list):
        atoms = functools.reduce(lambda x, y: x ^ y, scalars)
    else:
        atoms = scalars

    if multiline:
        NEWLINE = pp.Literal("\n").suppress()
        list_t = (
            START
            + pp.Optional(pp.delimitedList(atoms ^ NEWLINE, delim=delimiter))
            + END
        )
    else:
        list_t = START + pp.Optional(pp.delimitedList(atoms, delim=delimiter)) + END

    return list_t.addCondition(
        bool, message="Empty lists not allowed", fatal=throw_if_empty
    )


list_t = make_list_t(quoted_str_t ^ float_t ^ int_t ^ unquoted_str_t ^ bool_t)
