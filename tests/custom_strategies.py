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

from hypothesis import strategies as st


@st.composite
def floats(draw):
    """Generate floating point numbers in various formats.

    A composite testing strategy to generate floats in the formats
    understood by the `float_t` atom.
    """
    number = draw(st.floats(allow_nan=False, allow_infinity=False))
    fmt = draw(st.sampled_from(['{:.20f}', '{:.20e}', '{:.20E}', '{:+.20f}', '{:+.20e}', '{:+.20E}']))
    return fmt.format(number), number


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
