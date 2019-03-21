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
"""Tests for `parselglossy` package.

Tests checking predicates.
"""

import re
from contextlib import ExitStack as does_not_raise

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.validation import check_predicates


@pytest.fixture
def user():
    return {
        "scf": {
            "another_number": 10,
            "functional": "B3LYP",
            "max_num_iterations": 20,
            "some_acceleration": False,
            "some_complex_number": complex("0.0+0.0j"),
            "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
        },
        "title": "My title",
    }


testdata = [
    (
        {"scf": {"another_number": ["value < user['scf']['max_num_iterations']"]}},
        does_not_raise(),
    ),
    (
        {"scf": {"another_number": ["value =< user['scf']['max_num_iterations']"]}},
        pytest.raises(
            ParselglossyError,
            match=r"""Error(?:\(s\))? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+SyntaxError.*""",
        ),
    ),
    (
        {
            "scf": {
                "another_number": ["foo <= value < user['scf']['max_num_iterations']"]
            }
        },
        pytest.raises(
            ParselglossyError,
            match=r"""Error(?:\(s\))? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+NameError.*""",
        ),
    ),
    (
        {"scf": {"another_number": ["value < user['scf']['min_num_iterations']"]}},
        pytest.raises(
            ParselglossyError,
            match=r"""Error(?:\(s\))? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+KeyError.*""",
        ),
    ),
    (
        {
            "scf": {
                "another_number": [
                    "value < user['scf']['max_num_iterations'] / 'foooo'"
                ]
            }
        },
        pytest.raises(
            ParselglossyError,
            match=r"""Error(?:\(s\))? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+TypeError.*""",
        ),
    ),
    (
        {
            "title": ["len(value) < user['foo']"],
            "scf": {
                "another_number": [
                    "value / 'fooo' < 10",
                    "value < user['scf']['max_num_iterations']",
                ]
            },
        },
        pytest.raises(
            ParselglossyError,
            match=r"""Error(?:\(s\))? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+TypeError.*\n- At user\['title'\]:\s+KeyError.*""",
        ),
    ),
]


@pytest.mark.parametrize(
    "predicates,raises",
    testdata,
    ids=[
        "valid",
        "syntax_error",
        "name_error",
        "key_error",
        "type_error",
        "two_errors",
    ],
)
def test_check_predicates(user, predicates, raises):
    with raises:
        outgoing = check_predicates(incoming=user, predicates=predicates)
