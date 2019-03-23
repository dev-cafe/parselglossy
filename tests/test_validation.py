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
import re
from contextlib import ExitStack as does_not_raise
from pathlib import Path
from typing import List

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.utils import ComplexEncoder, as_complex
from parselglossy.validation import validate_from_dicts
from read_in import read_in


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
        "template_errors",
        "input.yml",
        "template_no_documentation.yml",
        pytest.raises(ParselglossyError),
        [
            r"- At user\['some_section'\]:\s+Sections must have a non-empty docstring\.\n"
            r"- At user\['some_section'\]\['a_short_string'\]:\s+Keywords must have a non-empty docstring\."
        ],
        None,
    ),
    (
        "template_errors",
        "input.yml",
        "template_empty_documentation.yml",
        pytest.raises(ParselglossyError),
        [
            r"- At user\['some_section'\]:\s+Sections must have a non-empty docstring\.\n"
            r"- At user\['some_section'\]\['a_short_string'\]:\s+Keywords must have a non-empty docstring\."
        ],
        None,
    ),
    (
        "template_errors",
        "input.yml",
        "template_invalid_predicate.yml",
        pytest.raises(ParselglossyError),
        [
            r"- At user\['some_section'\]\['a_short_string'\]:\s+NameError name 'undefined' is not defined in closure '0 < len\(value\) <= undefined'\."
        ],
        None,
    ),
]

input_errors_data = [
    (
        "input_errors",
        "unexpected_keyword.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [r"Error(?:s)? occurred when merging:\n- Found unexpected keyword: 'strange'"],
        None,
    ),
    (
        "input_errors",
        "unexpected_section.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [r"Error(?:s)? occurred when merging:\n- Found unexpected section: 'weird'"],
        None,
    ),
    (
        "input_errors",
        "input_missing_keyword.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when merging:\n- At user\['some_section'\]\['a_short_string'\]:\s+Keyword 'a_short_string' is required but has no value\."
        ],
        None,
    ),
    (
        "input_errors",
        "input_type_error_bool.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['some_feature'\]:\s+Actual \(int\) and declared \(bool\) types do not match\."
        ],
        None,
    ),
    (
        "input_errors",
        "input_type_error_float.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_float'\]:\s+Actual \(int\) and declared \(float\) types do not match\."
        ],
        None,
    ),
    (
        "input_errors",
        "input_type_error_int.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['some_number'\]:\s+Actual \(float\) and declared \(int\) types do not match\."
        ],
        None,
    ),
    (
        "input_errors",
        "input_type_error_list.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['some_list'\]:\s+Actual \(List\[float, float, int\]\) and declared \(List\[float\]\) types do not match\."
        ],
        None,
    ),
    (
        "input_errors",
        "input_type_error_str.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['a_short_string'\]:\s+Actual \(int\) and declared \(str\) types do not match\."
        ],
        None,
    ),
    (
        "input_errors",
        "input_predicate_intra.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['some_section'\]\['another_number'\]:\s+Predicate 'value % 2 == 0' not satisfied\."
        ],
        None,
    ),
    (
        "input_errors",
        "input_predicate_cross.yml",
        "template.yml",
        pytest.raises(ParselglossyError),
        [
            r"Error(?:s)? occurred when checking predicates:"
            r"\n- At user\['some_section'\]\['some_number'\]:\s+Predicate 'value < user\['some_section'\]\['another_number'\]' not satisfied\."
            r"\n- At user\['some_section'\]\['another_number'\]:\s+Predicate 'value > user\['some_section'\]\['some_number'\]' not satisfied\.",
            r"Error(?:s)? occurred when checking predicates:"
            r"\n- At user\['some_section'\]\['another_number'\]:\s+Predicate 'value > user\['some_section'\]\['some_number'\]' not satisfied\."
            r"\n- At user\['some_section'\]\['some_number'\]:\s+Predicate 'value < user\['some_section'\]\['another_number'\]' not satisfied\.",
        ],
        None,
    ),
]

validation_data = (
    [
        ("overall", "input.yml", "template.yml", does_not_raise(), valid(), [""]),
        (
            "overall",
            "default.yml",
            "template_with_default_section.yml",
            does_not_raise(),
            {"foobar": False, "foo": {"bar": False}},
            [""],
        ),
        (
            "overall",
            None,
            "template_all_default.yml",
            does_not_raise(),
            {"foobar": True, "foo": {"bar": False}},
            [""],
        ),
    ]
    + template_errors_data
    + input_errors_data
)


def ids(terms: List[str]) -> str:
    return "-".join([t.rsplit(".", 1)[0] if t is not None else "" for t in terms])


@pytest.mark.parametrize(
    "folder,input_file_name,template_file_name,raises,valid,error_message",
    [
        pytest.param(f, i, t, r, v, e, id=ids([f, i, t]))
        for f, i, t, r, v, e in validation_data
    ],
)
def test_validation(
    folder, input_file_name, template_file_name, raises, valid, error_message
):
    user, template = read_in(folder, input_file_name, template_file_name)

    with raises as e:
        # Validate and dump JSON
        dumped = Path("validated.json")
        user = validate_from_dicts(ir=user, template=template, fr_file=dumped)
        assert user == valid
        # Check error message is correct
        assert re.match("|".join(error_message), str(e)) is not None

        # Read JSON (round-trip check)
        with dumped.open("r") as v:
            validated = json.load(v, object_hook=as_complex)
        assert validated == valid
        dumped.unlink()
