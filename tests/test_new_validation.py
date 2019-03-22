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

import json
from contextlib import ExitStack as does_not_raise
from pathlib import Path
from typing import List

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.parselglossy import validate
from parselglossy.utils import as_complex
from read_in import read_in


@pytest.fixture
def valid():
    return {
        "title": "this is an example",
        "scf": {
            "functional": "B3LYP",
            "max_num_iterations": 20,
            "some_acceleration": True,
            "thresholds": {"some_integral_screening": 0.0002, "energy": 1e-05},
            "another_number": 10,
            "some_complex_number": complex(0.0, 0.0),
        },
    }


template_errors_data = [
    (
        "template_no_documentation.yml",
        ParselglossyError,
        "section(s) without any documentation: ['some_section']",
    ),
    (
        "template_empty_documentation.yml",
        ParselglossyError,
        "section(s) without any documentation: ['some_section']",
    ),
    (
        "template_invalid_predicate.yml",
        ParselglossyError,
        "error in predicate '0 < len(value) <= undefined' in keyword 'a_short_string'",
    ),
]

validation_data = [
    ("overall", "input.yml", "template.yml", does_not_raise()),
    (
        "template_errors",
        "input.yml",
        "template_no_documentation.yml",
        pytest.raises(
            ParselglossyError,
            match=r"- At user\['some_section'\]:\s+Sections must have a non-empty docstring\.\n"
            r"- At user\['some_section'\]\['a_short_string'\]:\s+Keywords must have a non-empty docstring\.",
        ),
    ),
    (
        "template_errors",
        "input.yml",
        "template_empty_documentation.yml",
        pytest.raises(
            ParselglossyError,
            match=r"- At user\['some_section'\]:\s+Sections must have a non-empty docstring\.\n"
            r"- At user\['some_section'\]\['a_short_string'\]:\s+Keywords must have a non-empty docstring\.",
        ),
    ),
    (
        "template_errors",
        "input.yml",
        "template_invalid_predicate.yml",
        pytest.raises(
            ParselglossyError,
            match=r"- At user\['some_section'\]\['a_short_string'\]:\s+NameError name 'undefined' is not defined in closure '0 < len\(user\['some_section'\]\['a_short_string'\]\) <= undefined'\.",
        ),
    ),
]


def ids(terms: List[str]) -> str:
    return "-".join([t.rsplit(".", 1)[0] for t in terms])


@pytest.mark.parametrize(
    "folder,input_file_name,template_file_name,raises",
    [pytest.param(f, i, t, r, id=ids([f, i, t])) for f, i, t, r in validation_data],
)
def test_new_validation(valid, folder, input_file_name, template_file_name, raises):
    user, template = read_in(folder, input_file_name, template_file_name)

    with raises:
        user = validate(dumpfr=True, ir=user, template=template)
        assert user == valid

    # Round-trip
    infile = Path("validated.json")
    with infile.open("r") as v:
        validated = json.load(v, object_hook=as_complex)
    assert validated == valid
