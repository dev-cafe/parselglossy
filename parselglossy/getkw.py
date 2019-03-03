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

import pyparsing as pp

from .atoms import bool_t, data_t, fortranStyleComment, num_t, str_t


def grammar():
    LBRACKET, RBRACKET, EQ, COMMA = map(pp.Suppress, '[]=,')
    NEWLINE = pp.Literal('\n').suppress()
    LBRACE, RBRACE = map(pp.Suppress, '{}')

    # Define key
    key = pp.Word(pp.alphas + '_<>', pp.alphanums + '_<>')

    # A scalar value (bool, int, float, complex, str)
    scalar = bool_t ^ num_t ^ str_t
    # An array value ([bool], [int], [float], [complex], [str])
    array = LBRACKET + pp.delimitedList(scalar ^ NEWLINE) + RBRACKET

    value = scalar ^ array

    # Define key-value pairs, i.e. our keywords
    pair = pp.Group(key + EQ + value)

    # Define values and section recursively
    section = pp.Forward()
    values = pp.Forward()
    section << pp.Group(key + LBRACE + values + RBRACE)
    values << pp.Dict(pp.OneOrMore(pair | data_t | section))

    # Define input
    input = pp.Dict(pp.OneOrMore(section))

    # Ignore Python (#), C/C++ (/* */ and //), and Fortran (!) style comments
    comment = pp.cppStyleComment | pp.pythonStyleComment | fortranStyleComment
    input.ignore(comment)

    return input
