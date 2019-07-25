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
"""LSDalton grammar generation."""

from typing import Any

import pyparsing as pp
from .atoms import fortranStyleComment, float_t, int_t, unquoted_str_t


def grammar_dal() -> Any:
    """The LSDalton *.dal grammar.

    Returns
    -------
    A parsing grammar.
    """

    # Define key
    word = pp.Word(pp.alphas, pp.alphanums + '_')
    word_with_space = pp.OneOrMore(word | pp.White(' ', max=1) + ~pp.White())

    key = pp.Combine('.' + word_with_space)
    star_section = pp.Combine('*' + word_with_space)
    star_star_section = pp.Combine('**' + word_with_space)

    NEWLINE = pp.LineEnd().suppress()

    scalar = float_t ^ int_t ^ unquoted_str_t
    pair = pp.Group(key + NEWLINE + scalar)

    section = pp.Group(star_section + NEWLINE + pp.Dict(pp.OneOrMore(pair)))

    supersection = pp.Group(
                       star_star_section + NEWLINE + pp.Dict(pp.OneOrMore(section))
                   )

    # Define input
    result = pp.Dict(pp.OneOrMore(supersection))

    # Ignore Python (#), C/C++ (/* */ and //), and Fortran (!) style comments
    comment = pp.pythonStyleComment | fortranStyleComment
    result.ignore(comment)

    return result
