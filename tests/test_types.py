# -*- coding: utf-8 -*-
#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2020 Roberto Di Remigio, Radovan Bast, and contributors.
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

"""Tests for `parselglossy` package."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from parselglossy.types import type_matches


@given(a=st.booleans())
def test_type_matches_bool(a):
    assert type_matches(a, "bool")
    assert not type_matches(0, "bool")


@given(a=st.text())
def test_type_matches_str(a):
    assert type_matches(a, "str")
    assert not type_matches(a, "int")
    assert not type_matches(a, "float")
    assert not type_matches(a, "complex")
    assert not type_matches(1.0, "str")


@given(a=st.integers())
def test_type_matches_int(a):
    assert type_matches(a, "int")
    assert not type_matches(a, "str")
    assert not type_matches(a, "float")
    assert not type_matches(a, "complex")


@given(a=st.floats(allow_nan=False, allow_infinity=False))
def test_type_matches_float(a):
    assert type_matches(a, "float")
    assert not type_matches(a, "str")
    assert not type_matches(a, "int")
    assert not type_matches(a, "complex")
    assert not type_matches(1, "float")


@given(a=st.complex_numbers(allow_nan=False, allow_infinity=False))
def test_type_matches_complex(a):
    assert type_matches(a, "complex")
    assert not type_matches(a, "str")
    assert not type_matches(a, "int")
    assert not type_matches(a, "float")


@given(a=st.lists(st.text(), min_size=1))
def test_type_matches_list_str(a):
    assert type_matches(a, "List[str]")
    assert not type_matches((1, 2, 3), "List[str]")
    assert not type_matches([1, 2, 3], "List[str]")
    assert not type_matches(["foo", 2, 3], "List[str]")
    assert not type_matches(a, "List[int]")
    assert not type_matches(a, "List[float]")
    assert not type_matches(a, "List[complex]")


@given(a=st.lists(st.integers(), min_size=1))
def test_type_matches_list_int(a):
    assert type_matches(a, "List[int]")
    assert not type_matches((1, 2, 3), "List[int]")
    assert not type_matches([1, "foo", 2, 3], "List[int]")
    assert not type_matches(a, "List[str]")
    assert not type_matches(a, "List[float]")
    assert not type_matches(a, "List[complex]")


@given(a=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_type_matches_list_float(a):
    assert type_matches(a, "List[float]")
    assert not type_matches((1, 2, 3), "List[float]")
    assert not type_matches([1, 2, 3], "List[float]")
    assert not type_matches([1.0, 2, 3], "List[float]")
    assert not type_matches(a, "List[str]")
    assert not type_matches(a, "List[int]")
    assert not type_matches(a, "List[complex]")


@given(
    a=st.lists(st.complex_numbers(allow_nan=False, allow_infinity=False), min_size=1)
)
def test_type_matches_list_complex(a):
    assert type_matches(a, "List[complex]")
    assert not type_matches((1 + 1j, 2 + 2j, 3 + 3j), "List[complex]")
    assert not type_matches([1, 2, 3], "List[complex]")
    assert not type_matches([1 + 1j, 2.0, 3], "List[complex]")
    assert not type_matches(a, "List[str]")
    assert not type_matches(a, "List[int]")
    assert not type_matches(a, "List[float]")


def test_type_matches_unexpected():
    with pytest.raises(ValueError):
        assert type_matches("example", "weird")
        assert type_matches("example", "List[strange]")
