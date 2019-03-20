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

Tests defaulting with a callable.
"""

import itertools
import re
from contextlib import ExitStack as does_not_raise

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.validation import fix_defaults


def noactions_raw():
    return {
        "scf": {
            "another_number": 10,
            "functional": None,
            "max_num_iterations": 20,
            "some_acceleration": False,
            "some_complex_number": "0.0 + 0.0j",
            "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
        },
        "title": None,
    }


noactions_ref = {
    "scf": {
        "another_number": 10,
        "functional": None,
        "max_num_iterations": 20,
        "some_acceleration": False,
        "some_complex_number": complex("0.0+0.0j"),
        "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
    },
    "title": None,
}


def actions_raw():
    return {
        "scf": {
            "another_number": "user['scf']['max_num_iterations'] / 10",
            "functional": None,
            "max_num_iterations": 20,
            "some_acceleration": False,
            "some_complex_number": "0.0 + 0.0j",
            "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
        },
        "title": None,
    }


actions_ref = {
    "scf": {
        "another_number": 2,
        "functional": None,
        "max_num_iterations": 20,
        "some_acceleration": False,
        "some_complex_number": complex("0.0+0.0j"),
        "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
    },
    "title": None,
}


def one_invalid_raw():
    return {
        "scf": {
            "another_number": "user['scf']['min_num_iterations'] / 2",
            "functional": "'B3LYP'",
            "max_num_iterations": 20,
            "some_acceleration": False,
            "some_complex_number": "0.0 + 0.0j",
            "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
        },
        "title": None,
    }


def two_invalid_raw():
    return {
        "scf": {
            "another_number": "user['scf']['min_num_iterations'] / 2",
            "functional": "'B3LYP' / 2",
            "max_num_iterations": 20,
            "some_acceleration": False,
            "some_complex_number": "0.0 + 0.0j",
            "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
        },
        "title": None,
    }


invalid_ref = {
    "scf": {
        "another_number": None,
        "functional": None,
        "max_num_iterations": 20,
        "some_acceleration": False,
        "some_complex_number": complex("0.0+0.0j"),
        "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
    },
    "title": None,
}


invalid_messages = [
    r"""Error(?:\(s\))? occurred when fixing defaults:\n- At user\['scf'\]\['another_number'\]:\s+KeyError 'min_num_iterations' in defaulting closure 'user\['scf'\]\['min_num_iterations'\] / 2'\.\n- At user\['scf'\]\['functional'\]:\s+TypeError unsupported operand type\(s\) for /: 'str' and 'int' in defaulting closure ''B3LYP' / 2'\.""",
    r"""Error(?:\(s\))? occurred when fixing defaults:\n- At user\['scf'\]\['functional'\]:\s+TypeError unsupported operand type\(s\) for /: 'str' and 'int' in defaulting closure ''B3LYP' / 2'\.\n- At user\['scf'\]\['another_number'\]:\s+KeyError 'min_num_iterations' in defaulting closure 'user\['scf'\]\['min_num_iterations'\] / 2'\.
    """,
]

testdata = [
    (noactions_raw(), noactions_ref, does_not_raise()),
    (actions_raw(), actions_ref, does_not_raise()),
    (
        one_invalid_raw(),
        invalid_ref,
        pytest.raises(
            ParselglossyError,
            match=r"""Error(?:\(s\))? occurred when fixing defaults:\n- At user\['scf'\]\['another_number'\]:\s+KeyError 'min_num_iterations' in defaulting closure 'user\['scf'\]\['min_num_iterations'\] / 2'""",
        ),
    ),
    (
        two_invalid_raw(),
        invalid_ref,
        pytest.raises(
            ParselglossyError, match=re.compile("({0}|{1})".format(*invalid_messages))
        ),
    ),
]


@pytest.mark.parametrize(
    "readin,ref,raises",
    testdata,
    ids=["noactions", "actions", "one_invalid", "two_invalid_raw"],
)
def test_fix_defaults(readin, ref, raises):
    with raises:
        outgoing = fix_defaults(readin)
        assert outgoing == ref
