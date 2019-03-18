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

Tests merging of template and user input `dict`-s into an unvalidated input `dict`.
"""

from pathlib import Path

import pytest

from parselglossy.read_yaml import read_yaml_file
from parselglossy.validate import merge_ours

reference = {
    "title": "this is an example",
    "scf": {
        "functional": "B3LYP",
        "max_num_iterations": 20,
        "some_acceleration": True,
        "thresholds": {"some_integral_screening": 0.0002, "energy": 1e-05},
        "another_number": 10,
        "some_complex_number": "0.0+0.0j",
    },
}


@pytest.fixture
def template():
    defaults = {
        "scf": {
            "another_number": 10,
            "functional": None,
            "max_num_iterations": 20,
            "some_acceleration": False,
            "some_complex_number": "0.0+0.0j",
            "thresholds": {"energy": 0.001, "some_integral_screening": 0.0001},
        },
        "title": None,
    }
    return defaults


def test_merge(template):
    this_path = Path(__file__).parent
    input_file = this_path / "validation" / "overall" / "input.yml"
    user = read_yaml_file(input_file)

    outgoing = merge_ours(theirs=template, ours=user)

    assert outgoing == reference
