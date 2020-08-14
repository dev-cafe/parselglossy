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

Tests checking predicates.
"""

import re
from contextlib import ExitStack as does_not_raise
from copy import deepcopy

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


empty_predicates = {
    "scf": {
        "another_number": None,
        "functional": None,
        "max_num_iterations": None,
        "some_acceleration": None,
        "some_complex_number": None,
        "thresholds": {"energy": None, "some_integral_screening": None},
    },
    "title": None,
}


def valid_predicates():
    d = deepcopy(empty_predicates)
    d["scf"]["another_number"] = ["value < user['scf']['max_num_iterations']"]
    return d


def failing_predicates():
    d = deepcopy(empty_predicates)
    d["scf"]["another_number"] = ["value % 3 == 0"]
    return d


def syntax_error_predicates():
    d = deepcopy(empty_predicates)
    d["scf"]["another_number"] = ["value =< user['scf']['max_num_iterations']"]
    return d


def name_error_predicates():
    d = deepcopy(empty_predicates)
    d["scf"]["another_number"] = ["foo <= value < user['scf']['max_num_iterations']"]
    return d


def key_error_predicates():
    d = deepcopy(empty_predicates)
    d["scf"]["another_number"] = ["value < user['scf']['min_num_iterations']"]
    return d


def type_error_predicates():
    d = deepcopy(empty_predicates)
    d["scf"]["another_number"] = ["value < user['scf']['max_num_iterations'] / 'foooo'"]
    return d


def multiple_errors_predicates():
    d = deepcopy(empty_predicates)
    d["title"] = ["len(value) < user['foo']"]
    d["scf"]["another_number"] = [
        "value / 'fooo' < 10",
        "value < user['scf']['max_num_iterations']",
    ]
    return d


testdata = [
    (valid_predicates(), None, [""]),
    (
        failing_predicates(),
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+Predicate 'value % 3 == 0' not satisfied\."
        ],
    ),
    (
        syntax_error_predicates(),
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+SyntaxError.*"
        ],
    ),
    (
        name_error_predicates(),
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+NameError.*"
        ],
    ),
    (
        key_error_predicates(),
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+KeyError.*"
        ],
    ),
    (
        type_error_predicates(),
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+TypeError.*"
        ],
    ),
    (
        multiple_errors_predicates(),
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['scf'\]\['another_number'\]:\s+TypeError.*\n- At user\['title'\]:\s+KeyError.*",
            r"Error(?:s)? occurred when checking predicates:\n- At user\['title'\]:\s+KeyError.*\n- At user\['scf'\]\['another_number'\]:\s+TypeError.*",
        ],
    ),
]


@pytest.mark.parametrize(
    "predicates,raises,error_message",
    testdata,
    ids=[
        "valid",
        "failing",
        "syntax_error",
        "name_error",
        "key_error",
        "type_error",
        "two_errors",
    ],
)
def test_check_predicates(user, predicates, raises, error_message):
    if raises is None:
        ctx = does_not_raise()
    else:
        ctx = pytest.raises(ParselglossyError, match="|".join(error_message))

    with ctx:
        check_predicates(incoming=user, predicates=predicates)
