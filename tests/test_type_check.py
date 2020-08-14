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

"""Tests for `parselglossy` package.

Tests type checking and type fixation.
"""

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.validation import fix_defaults


@pytest.fixture
def types():
    return {
        "title": "str",
        "some_float": "float",
        "some_section": {
            "a_short_string": "str",
            "some_number": "int",
            "another_number": "int",
            "some_feature": "bool",
            "some_list": "List[float]",
            "some_complex": "complex",
        },
    }


def type_error_bool():
    d = {
        "title": "this is my title",
        "some_float": 2.4,
        "some_section": {
            "a_short_string": "short",
            "some_number": 7,
            "another_number": 20,
            "some_feature": 1,
            "some_list": [1.0, 2.0, 3.0],
            "some_complex": complex(0.0, 1.0),
        },
    }

    n = "type_error_bool"
    e = r"""
Error occurred when fixing defaults:
- At user\['some_section'\]\['some_feature'\]:
  Actual \(int\) and declared \(bool\) types do not match\."""

    return d, n, e


def type_error_float():
    d = {
        "title": "this is my title",
        "some_float": 2,
        "some_section": {
            "a_short_string": "short",
            "some_number": 7,
            "another_number": 20,
            "some_feature": True,
            "some_list": [1.0, 2.0, 3.0],
            "some_complex": complex(0.0, 1.0),
        },
    }
    n = "type_error_float"
    e = r"""
Error occurred when fixing defaults:
- At user\['some_float'\]:
  Actual \(int\) and declared \(float\) types do not match\."""

    return d, n, e


def type_error_int():
    d = {
        "title": "this is my title",
        "some_float": 2.4,
        "some_section": {
            "a_short_string": "short",
            "some_number": 7.0,
            "another_number": 20,
            "some_feature": True,
            "some_list": [1.0, 2.0, 3.0],
            "some_complex": complex(0.0, 1.0),
        },
    }
    n = "type_error_int"
    e = r"""
Error occurred when fixing defaults:
- At user\['some_section'\]\['some_number'\]:
  Actual \(float\) and declared \(int\) types do not match\."""

    return d, n, e


def type_error_list():
    d = {
        "title": "this is my title",
        "some_float": 2.4,
        "some_section": {
            "a_short_string": "short",
            "some_number": 7,
            "another_number": 20,
            "some_feature": True,
            "some_list": [1.0, 2.0, 3],
            "some_complex": complex(0.0, 1.0),
        },
    }
    n = "type_error_list"
    e = r"""
Error occurred when fixing defaults:
- At user\['some_section'\]\['some_list'\]:
  Actual \(List\[float, float, int\]\) and declared \(List\[float\]\) types do not match\."""

    return d, n, e


def type_error_str():
    d = {
        "title": "this is my title",
        "some_float": 2.4,
        "some_section": {
            "a_short_string": 0,
            "some_number": 7,
            "another_number": 20,
            "some_feature": True,
            "some_list": [1.0, 2.0, 3.0],
            "some_complex": complex(0.0, 1.0),
        },
    }
    n = "type_error_str"
    e = r"""
Error(?:s)? occurred when fixing defaults:
- At user\['some_section'\]\['a_short_string'\]:
  Actual \(int\) and declared \(str\) types do not match\."""

    return d, n, e


type_checking_data = [
    type_error_bool(),
    type_error_float(),
    type_error_int(),
    type_error_list(),
    type_error_str(),
]


@pytest.mark.parametrize(
    "user,error_message", [pytest.param(d, e, id=n) for d, n, e in type_checking_data]
)
def test_input_errors(types, user, error_message):
    with pytest.raises(ParselglossyError, match=error_message):
        outgoing = fix_defaults(user, types=types)
