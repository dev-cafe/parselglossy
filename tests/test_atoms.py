#!/usr/bin/env python

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
"""Tests for `parselglossy` package."""

import string

import pytest
from hypothesis import given
from hypothesis import strategies as st

from parselglossy.grammars import atoms


@given(a=st.sampled_from(atoms.truthy + atoms.falsey))
def test_atom_bool(a):
    tokens = atoms.bool_t.parseString('{:s}'.format(a)).asList()
    assert tokens[0] == atoms.to_bool(a)


@given(a=st.integers())
def test_atoms_int(a):
    tokens = atoms.int_t.parseString('{:d}'.format(a)).asList()
    assert tokens[0] == a


@st.composite
def floats(draw):
    """Generate floating point numbers in various formats.

    A composite testing strategy to generate floats in the formats
    understood by the `float_t` atom.
    """
    number = draw(st.floats(allow_nan=False, allow_infinity=False))
    fmt = draw(st.sampled_from(['{:.20f}', '{:.20e}', '{:.20E}', '{:+.20f}', '{:+.20e}', '{:+.20E}']))
    return fmt.format(number), number


@given(a=floats())
def test_atoms_float(a):
    tokens = atoms.float_t.parseString(a[0]).asList()
    assert tokens[0] == pytest.approx(a[1])


@given(a=st.text(alphabet=(string.digits + string.ascii_letters), min_size=1))
def test_atoms_str(a):
    tokens = atoms.str_t.parseString('{:s}'.format(a)).asList()
    assert tokens[0] == a


@st.composite
def complex_numbers(draw):
    """Generate complex numbers in various formats.

    A composite testing strategy to generate complex numbers in the formats
    understood by the `complex_t` atom.
    """
    number = draw(st.complex_numbers(allow_nan=False, allow_infinity=False))
    has_real = draw(st.booleans())
    w_space = draw(st.booleans())
    real_fmt = draw(st.sampled_from(['{:.20g}', '{:.20G}']))
    imag_fmt = draw(st.sampled_from(['{:+.20g}*j', '{:+.20G}*j', '{:+.20g}*J', '{:+.20G}*J']))
    number_as_string = ''
    if has_real:
        if w_space:
            fmt = real_fmt + ' ' + imag_fmt
        else:
            fmt = real_fmt + imag_fmt
        number_as_string = fmt.format(number.real, number.imag)
    else:
        number = complex(0.0, number.imag)
        fmt = imag_fmt
        number_as_string = fmt.format(number.imag)
    return number_as_string, number


@given(a=complex_numbers())
def test_atoms_complex(a):
    tokens = atoms.complex_t.parseString(a[0]).asList()
    assert tokens[0] == pytest.approx(a[1])


@given(
    a=st.sampled_from([['raw', 'H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n'],
                       ['RAW',
                        'H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n']]).map(lambda x: ('${0:s}\n{1:s}$end'.format(x[0], x[1]), x)))
def test_atoms_data(a):
    tokens = atoms.data_t.parseString(a[0]).asList()
    assert tokens[0] == a[1]
