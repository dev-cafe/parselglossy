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

import json
from contextlib import ExitStack as does_not_raise
from pathlib import Path
from typing import List

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.utils import as_complex
from parselglossy.check_template import is_template_valid
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
        ParselglossyError,
        None,
        [
            r"- At user\['some_section'\]:\s+Sections must have a non-empty docstring\.\n"
            r"- At user\['some_section'\]\['a_short_string'\]:\s+Keywords must have a non-empty docstring\."
        ],
    ),
    (
        "template_errors",
        "input.yml",
        "template_empty_documentation.yml",
        ParselglossyError,
        None,
        [
            r"- At user\['some_section'\]:\s+Sections must have a non-empty docstring\.\n"
            r"- At user\['some_section'\]\['a_short_string'\]:\s+Keywords must have a non-empty docstring\."
        ],
    ),
    (
        "template_errors",
        "input.yml",
        "template_invalid_predicate.yml",
        ParselglossyError,
        None,
        [
            r"- At user\['some_section'\]\['a_short_string'\]:\s+NameError name 'undefined' is not defined in closure '0 < len\(value\) <= undefined'\."
        ],
    ),
    (
        "template_errors",
        "input.yml",
        "template_w_cycles.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when checking the template:\s+- At user\['(some|another)_section'\]\['(some|another)_number'\]:\s+Keyword depends cyclically on keyword user\['(some|another)_section'\]\['(some|another)_number'\]"
        ],
    ),
]

input_errors_data = [
    (
        "input_errors",
        "unexpected_keyword.yml",
        "template.yml",
        ParselglossyError,
        None,
        [r"Error(?:s)? occurred when merging:\n- Found unexpected keyword: 'strange'"],
    ),
    (
        "input_errors",
        "unexpected_section.yml",
        "template.yml",
        ParselglossyError,
        None,
        [r"Error(?:s)? occurred when merging:\n- Found unexpected section: 'weird'"],
    ),
    (
        "input_errors",
        "input_missing_keyword.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when merging:\n- At user\['some_section'\]\['a_short_string'\]:\s+Keyword 'a_short_string' is required but has no value\."
        ],
    ),
    (
        "input_errors",
        "input_type_error_bool.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['some_feature'\]:\s+Actual \(int\) and declared \(bool\) types do not match\."
        ],
    ),
    (
        "input_errors",
        "input_type_error_float.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_float'\]:\s+Actual \(int\) and declared \(float\) types do not match\."
        ],
    ),
    (
        "input_errors",
        "input_type_error_int.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['some_number'\]:\s+Actual \(float\) and declared \(int\) types do not match\."
        ],
    ),
    (
        "input_errors",
        "input_type_error_list.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['some_list'\]:\s+Actual \(List\[float, float, int\]\) and declared \(List\[float\]\) types do not match\."
        ],
    ),
    (
        "input_errors",
        "input_type_error_str.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when fixing defaults:\n- At user\['some_section'\]\['a_short_string'\]:\s+Actual \(int\) and declared \(str\) types do not match\."
        ],
    ),
    (
        "input_errors",
        "input_predicate_intra.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when checking predicates:\n- At user\['some_section'\]\['another_number'\]:\s+Predicate 'value % 2 == 0' not satisfied\."
        ],
    ),
    (
        "input_errors",
        "input_predicate_cross.yml",
        "template.yml",
        ParselglossyError,
        None,
        [
            r"Error(?:s)? occurred when checking predicates:"
            r"\n- At user\['some_section'\]\['some_number'\]:\s+Predicate 'value < user\['some_section'\]\['another_number'\]' not satisfied\."
            r"\n- At user\['some_section'\]\['another_number'\]:\s+Predicate 'value > user\['some_section'\]\['some_number'\]' not satisfied\.",
            r"Error(?:s)? occurred when checking predicates:"
            r"\n- At user\['some_section'\]\['another_number'\]:\s+Predicate 'value > user\['some_section'\]\['some_number'\]' not satisfied\."
            r"\n- At user\['some_section'\]\['some_number'\]:\s+Predicate 'value < user\['some_section'\]\['another_number'\]' not satisfied\.",
        ],
    ),
]

validation_data = (
    [
        ("overall", "input.yml", "template.yml", None, valid(), [""]),
        (
            "overall",
            "default.yml",
            "template_with_default_section.yml",
            None,
            {"foobar": False, "foo": {"bar": False}},
            [""],
        ),
        (
            "overall",
            None,
            "template_all_default.yml",
            None,
            {"foobar": True, "foo": {"bar": False}},
            [""],
        ),
        (
            "overall",
            "input_ordering.yml",
            "ordering.yml",
            None,
            {
                "flavor": 2.0,
                "color": 2.0,
                "charge": 2.0,
                "spectator": "nothing to see",
                "adorable_kitten": {"flavor": 1.0, "color": 1.5, "charge": 1.0,},
            },
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

    if raises is None:
        ctx = does_not_raise()
    else:
        ctx = pytest.raises(ParselglossyError, match="|".join(error_message))

    with ctx:
        # Validate and dump JSON
        dumped = Path("validated.json")
        template = is_template_valid(template)
        user = validate_from_dicts(ir=user, template=template, fr_file=dumped)
        assert user == valid

        # Read JSON (round-trip check)
        with dumped.open("r") as v:
            validated = json.load(v, object_hook=as_complex)
        assert validated == valid
        dumped.unlink()
