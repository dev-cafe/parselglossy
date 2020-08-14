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

Tests defaulting:
  - Required keywords that are absent report errors.
  - Invalid callables report errors.

To test, we create a fixture with the types and a valid reference dictionary.
We then proceed to create copies of the reference and modify some of its
values, to see whether we fix back defaults correctly.
"""

import re
from contextlib import ExitStack as does_not_raise
from copy import deepcopy

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.validation import fix_defaults


def valid():
    return {
        "scf": {
            "another_number": 10,
            "functional": "B3LYP",
            "max_num_iterations": 20,
            "some_acceleration": False,
            "list_complex_number": [complex("0.0+0.0j"), complex("1.0+0.5j")],
            "thresholds": {
                "some_complex_number": complex("0.0+0.0j"),
                "energy": 0.001,
                "some_integral_screening": 0.0001,
            },
        },
        "list_of_strings": ["foo", "bar"],
        "title": "My fantastic calculation",
    }


@pytest.fixture
def types():
    return {
        "scf": {
            "another_number": "int",
            "functional": "str",
            "max_num_iterations": "int",
            "some_acceleration": "bool",
            "list_complex_number": "List[complex]",
            "thresholds": {
                "some_complex_number": "complex",
                "energy": "float",
                "some_integral_screening": "float",
            },
        },
        "list_of_strings": "List[str]",
        "title": "str",
    }


raw = {
    "scf": {
        "another_number": 10,
        "functional": "B3LYP",
        "max_num_iterations": 20,
        "some_acceleration": False,
        "list_complex_number": ["0.0+0.0j", "1.0+0.5j"],
        "thresholds": {
            "some_complex_number": "0.0+0.0j",
            "energy": 0.001,
            "some_integral_screening": 0.0001,
        },
    },
    "list_of_strings": ["foo", "bar"],
    "title": "My fantastic calculation",
}


def valid_with_action():
    d = deepcopy(raw)
    d["scf"]["another_number"] = "user['scf']['max_num_iterations'] / 10"
    r = valid()
    r["scf"]["another_number"] = 2
    return d, r


def one_invalid_action():
    d = deepcopy(raw)
    d["scf"]["another_number"] = "user['scf']['min_num_iterations'] / 2"
    return d


def type_error_action():
    d = deepcopy(raw)
    d["scf"]["another_number"] = "user['title'] / 2"
    return d


def two_invalid_actions():
    d = deepcopy(raw)
    d["scf"]["another_number"] = "user['scf']['min_num_iterations'] / 2"
    d["scf"]["thresholds"]["energy"] = "10 * False"
    return d


error_preamble = r"Error(?:s)? occurred when fixing defaults:\n"

msg1 = r"- At user\['scf'\]\['another_number'\]:\s+KeyError 'min_num_iterations' in closure 'user\['scf'\]\['min_num_iterations'\] / 2'\."

msg2 = r"- At user\['scf'\]\['thresholds'\]\['energy'\]:\s+Actual \(str\) and declared \(float\) types do not match\."

# We need to check against two possible orderings of the error message.
# In Python 3.5 orderings of dict is not guaranteed!
invalid_messages = [
    error_preamble + msg1 + r"\n" + msg2,
    error_preamble + msg2 + r"\n" + msg1,
]

msg3 = r"- At user\['scf'\]\['another_number'\]:\s+TypeError unsupported operand type\(s\) for /: 'str' and 'int' in closure 'user\['title'\] / 2'\."

testdata = [
    (raw, valid(), does_not_raise(), [""]),
    (*valid_with_action(), does_not_raise(), [""]),
    (
        one_invalid_action(),
        valid(),
        pytest.raises(ParselglossyError),
        [error_preamble + msg1],
    ),
    (
        type_error_action(),
        valid(),
        pytest.raises(ParselglossyError),
        [error_preamble + msg3],
    ),
    (
        two_invalid_actions(),
        valid(),
        pytest.raises(ParselglossyError),
        invalid_messages,
    ),
]


@pytest.mark.parametrize(
    "user,ref,raises,error_message",
    testdata,
    ids=[
        "noactions",
        "valid_action",
        "one_invalid_action",
        "type_error_action",
        "two_invalid_actions",
    ],
)
def test_fix_defaults(types, user, ref, raises, error_message):
    with raises as e:
        outgoing = fix_defaults(user, types=types)
        assert outgoing == ref
        # Check error message is correct
        assert re.match("|".join(error_message), str(e)) is not None
