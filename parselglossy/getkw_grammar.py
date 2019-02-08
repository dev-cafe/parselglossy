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
# Roberto Di Remigio, and contributors. OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For information on the complete list of contributors to the
# parselglossy library, see: <http://parselglossy.readthedocs.io/>
#

import pyparsing as pp

from .atoms import bool_t, data_t, num_t, str_t


def getkw():
    LBRACKET, RBRACKET, EQ, COMMA = map(pp.Suppress, "[]=,")
    NEWLINE = pp.Literal('\n').suppress()

    _name = pp.Word(pp.alphas + '_', pp.alphanums + '_')
    _key = _name + EQ

    # A scalar value (bool, int, float, complex, str)
    scalar = bool_t ^ num_t ^ str_t
    # An array value ([bool], [int], [float], [complex], [str])
    array = LBRACKET + pp.delimitedList(scalar ^ NEWLINE) + RBRACKET

    _value = scalar ^ array

    kv_dict = pp.Dict(pp.OneOrMore(pp.Group(_key + _value)))
    grammar = pp.OneOrMore(pp.Group(data_t) | pp.Group(kv_dict))('getkw')

    return grammar


def flatten_dict(pp_dict):
    """
    pyparsing will generate a dictionary with key 'getkw' to contain all our
    results. key-value pairs are stored in sub-dictionaries, whereas raw data
    will appear as a list with one tuple as element.
    """
    parsed = {}
    for el in pp_dict['getkw']:
        if isinstance(el, dict):
            parsed.update(el)
        elif isinstance(el, list):
            parsed.update({el[0][0]: el[0][1]})
    return parsed
