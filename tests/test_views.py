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

Tests different views of validation specifications in YAML files.
"""

from contextlib import ExitStack as does_not_raise
from pathlib import Path

import pytest

from parselglossy import views
from parselglossy.yaml_utils import read_yaml_file

types = {
    "scf": {
        "functional": "str",
        "max_num_iterations": "int",
        "some_acceleration": "bool",
        "thresholds": {"some_integral_screening": "float", "energy": "float"},
        "another_number": "int",
        "some_complex_number": "complex",
    },
    "title": "str",
}

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

docstrings = {
    "scf": {
        "another_number": "Testing an even number in some range.",
        "functional": "XC functional.\n"
        "We also test that the string contains max 80 "
        "characters.",
        "max_num_iterations": "Max number of iterations.",
        "some_acceleration": "Turn on the new amazing acceleration " "scheme.",
        "some_complex_number": "Testing input with a complex number.",
        "thresholds": {
            "energy": "Some energy based threshold.",
            "some_integral_screening": "Some integral " "based " "threshold.",
        },
    },
    "title": "Title of the calculation.\n"
    "Since there is no default, this keyword is required.",
}

predicates = {
    "scf": {
        "another_number": [
            "0 <= value <= 40",
            "value % 2 == 0",
            "user['scf']['some_acceleration'] " "== True",
        ],
        "functional": ["len(value) <= 80"],
        "max_num_iterations": None,
        "some_acceleration": None,
        "some_complex_number": None,
        "thresholds": {"energy": None, "some_integral_screening": None},
    },
    "title": None,
}


@pytest.fixture
def template():
    this_path = Path(__file__).parent
    template_file = this_path / "validation" / "overall" / "template.yml"
    return read_yaml_file(template_file)


testdata = [
    (views.view_by_type, types, does_not_raise()),
    (views.view_by_default, defaults, does_not_raise()),
    (views.view_by_docstring, docstrings, does_not_raise()),
    (views.view_by_predicates, predicates, does_not_raise()),
    (lambda x: views.view_by("foobar", x), {}, pytest.raises(ValueError)),
]


@pytest.mark.parametrize(
    "viewer,reference,raises",
    testdata,
    ids=["types", "defaults", "docstrings", "predicates", "invalid"],
)
def test_view_by(template, viewer, reference, raises):
    with raises:
        view = viewer(template)
        assert view == reference
