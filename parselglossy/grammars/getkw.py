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
"""Getkw grammar generation."""

from typing import Any

import pyparsing as pp

from .atoms import (
    bool_t,
    complex_t,
    data_t,
    float_t,
    fortranStyleComment,
    int_t,
    make_list_t,
    quoted_str_t,
    unquoted_str_t,
)


def grammar(*, has_complex: bool = False) -> Any:
    """The Getkw recursive grammar.

    Parameters
    ----------
    has_complex: bool
        Whether to include complex numbers. Defaults to `False`.

    Returns
    -------
    A parsing grammar.
    """

    EQ, COMMA = map(pp.Suppress, "=,")
    LBRACE, RBRACE = map(pp.Suppress, "{}")

    # Define key
    key = pp.Word(pp.alphas + "_<>", pp.alphanums + "_<>")

    # A scalar value (bool, int, float, str)
    if has_complex:
        scalar = quoted_str_t ^ complex_t ^ float_t ^ int_t ^ bool_t ^ unquoted_str_t
    else:
        scalar = quoted_str_t ^ float_t ^ int_t ^ bool_t ^ unquoted_str_t
    # Coerce lists to be lists
    list_t = make_list_t(scalar)
    list_t.setParseAction(lambda t: [t])

    # Define key-value pairs, i.e. our keywords
    pair = pp.Group(key + EQ + list_t) | pp.Group(key + EQ + scalar)

    # Define values and section recursively
    section = pp.Forward()
    values = pp.Forward()
    section << pp.Group(key + LBRACE + values + RBRACE)
    values << pp.Dict(pp.OneOrMore(section | data_t | pair))

    # Define input
    retval = pp.Dict(pp.OneOrMore(section) | pp.OneOrMore(values))

    # Ignore Python (#), C/C++ (/* */ and //), and Fortran (!) style comments
    comment = pp.cppStyleComment | pp.pythonStyleComment | fortranStyleComment
    retval.ignore(comment)

    return retval
