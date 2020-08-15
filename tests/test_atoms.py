#!/usr/bin/env python
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

from string import ascii_letters, digits

import pytest
from hypothesis import example, given
from hypothesis import strategies as st
from pyparsing import ParseBaseException

from custom_strategies import (
    complex_numbers,
    floats,
    list_of_complex_numbers,
    list_of_floats,
    list_of_unquoted_str,
    unquoted_str,
)
from parselglossy.grammars import atoms

PRINTABLE = ascii_letters + digits + r"!#$%&*+-./:;<>?@^_|~"
"""str: Custom printable character set.

The printable character set is the standard set in `string.printable` minus
"\'(),=[\\]`{} and all whitespace characters.
"""


@given(a=st.sampled_from(atoms.TRUTHY + atoms.FALSEY))
def test_atom_bool(a):
    tokens = atoms.bool_t.parseString(f"{a:s}").asList()
    assert tokens[0] == atoms.to_bool(a)


@given(a=st.integers())
def test_atoms_int(a):
    tokens = atoms.int_t.parseString(f"{a:d}").asList()
    assert tokens[0] == a


@given(a=floats())
def test_atoms_float(a):
    tokens = atoms.float_t.parseString(a.string).asList()
    assert tokens[0] == pytest.approx(a.value)


@given(a=unquoted_str())
@example(a="foo_BAR")
@example(a="_123rdfoo_BAR")
def test_atoms_unquoted_str(a):
    tokens = atoms.unquoted_str_t.parseString(a).asList()
    assert tokens[0] == a


@pytest.mark.parametrize(
    "quoting", ["'{:s}'", '"{:s}"'], ids=["single_quotes", "double_quotes"]
)
@given(a=st.text(alphabet=(PRINTABLE + " "), min_size=1))
@example(a="Bobson Dugnutt")
@example(a="Glenallen    Mixon   ")
@example(a="    Todd Bonzalez   ")
@example(a="Dwigt Rortugal")
@example(a="Raul_Chamgerlain    ")
def test_atoms_quoted_str(a, quoting):
    tokens = atoms.quoted_str_t.parseString(quoting.format(a)).asList()
    assert tokens[0] == a


@given(a=complex_numbers())
def test_atoms_complex(a):
    tokens = atoms.complex_t.parseString(a.string).asList()
    assert tokens[0] == pytest.approx(a.value)


@given(
    a=st.sampled_from(
        [
            ["raw", "H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n"],
            ["RAW", "H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n"],
        ]
    ).map(lambda x: ("${0:s}\n{1:s}$end".format(x[0], x[1]), x))
)
def test_atoms_data(a):
    tokens = atoms.data_t.parseString(a[0]).asList()
    assert tokens[0] == a[1]


@pytest.mark.parametrize("a", ["[]", "[       ]", "[\n]"])
def test_list_empty(a):
    with pytest.raises(ParseBaseException, match=r"^Empty lists not allowed"):
        _ = atoms.list_t.parseString(f"{a}").asList()


@given(a=st.lists(st.integers(), min_size=1))
def test_list_int(a):
    tokens = atoms.list_t.parseString(f"{a}").asList()
    assert tokens == a


@given(a=list_of_floats())
def test_list_float(a):
    tokens = atoms.list_t.parseString(a.string).asList()
    assert tokens == pytest.approx(a.value)


@given(a=list_of_unquoted_str())
def test_list_unquoted_str(a):
    tokens = atoms.list_t.parseString(a.string).asList()
    assert tokens == a.value


@pytest.mark.parametrize(
    "quoting", ["'{:s}'", '"{:s}"'], ids=["single_quotes", "double_quotes"]
)
@given(a=st.lists(st.text(alphabet=(PRINTABLE)), min_size=1))
def test_list_quoted_str(a, quoting):
    example = "[" + ", ".join([quoting.format(x) for x in a]) + "]"
    tokens = atoms.list_t.parseString(example).asList()
    assert tokens == a


@given(a=list_of_complex_numbers())
def test_list_complex(a):
    scalar = (
        atoms.quoted_str_t
        ^ atoms.complex_t
        ^ atoms.float_t
        ^ atoms.int_t
        ^ atoms.unquoted_str_t
        ^ atoms.bool_t
    )
    list_t = atoms.make_list_t(scalar)
    tokens = list_t.parseString(a.string).asList()
    assert tokens == pytest.approx(a.value)
