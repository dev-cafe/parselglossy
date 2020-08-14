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

Tests merging of template and user input `dict`-s into an unvalidated input `dict`.
"""

from typing import Optional

import pytest

from parselglossy.exceptions import ParselglossyError
from parselglossy.validation import merge_ours
from parselglossy.views import view_by_default
from read_in import read_in

expected_data = [
    (
        "overall",
        "input.yml",
        "template.yml",
        {
            "scf": {
                "another_number": 10,
                "functional": "B3LYP",
                "max_num_iterations": 20,
                "some_acceleration": True,
                "some_complex_number": "0.0+0.0j",
                "thresholds": {"energy": 1.0e-5, "some_integral_screening": 0.0002},
            },
            "title": "this is an example",
        },
    ),
    (
        "overall",
        "default.yml",
        "template_with_default_section.yml",
        {"foobar": False, "foo": {"bar": False}},
    ),
    (
        "overall",
        None,
        "template_all_default.yml",
        {"foobar": True, "foo": {"bar": False}},
    ),
]


def expected_ids(name: Optional[str]) -> str:
    if name is None:
        id = "all_default"
    else:
        id = name.rsplit(".", 1)[0]
    return id


@pytest.mark.parametrize(
    "folder,user,template,ref",
    [pytest.param(*args, id=expected_ids(args[1])) for args in expected_data],
)
def test_merge_expected(folder, user, template, ref):
    user, template = read_in(folder, user, template)
    outgoing = merge_ours(theirs=view_by_default(template), ours=user)

    assert outgoing == ref


unexpected_data = [
    (
        "input_missing_keyword.yml",
        r"Error(?:s)? occurred when merging:\n- At user\['some_section'\]\['a_short_string'\]:\s+Keyword 'a_short_string' is required but has no value\.",
    ),
    (
        "unexpected_keyword.yml",
        r"Error(?:s)? occurred when merging:\n- Found unexpected keyword: 'strange'",
    ),
    (
        "unexpected_section.yml",
        r"Error(?:s)? occurred when merging:\n- Found unexpected section: 'weird'",
    ),
    (
        "unexpected_keyword_in_section.yml",
        r"Error(?:s)? occurred when merging:\n- Found unexpected keyword: 'strange'",
    ),
    (
        "unexpected_section_nested.yml",
        r"Error(?:s)? occurred when merging:\n- Found unexpected section: 'weird'",
    ),
]


@pytest.mark.parametrize(
    "input_file_name,error_message",
    [pytest.param(*args, id=expected_ids(args[0])) for args in unexpected_data],
)
def test_merge_unexpected(input_file_name, error_message):
    user, template = read_in("input_errors", input_file_name, "template.yml")

    with pytest.raises(ParselglossyError, match=error_message):
        outgoing = merge_ours(
            theirs=view_by_default(template), ours=user
        )  # type: Optional[JSONDict]
