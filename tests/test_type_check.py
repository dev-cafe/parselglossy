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

Tests type checking and type fixation.
"""

import pytest
from parselglossy import views
from parselglossy.exceptions import ParselglossyError
from parselglossy.types import typenade
from parselglossy.validation import merge_ours
from read_in import read_in

type_checking_data = [
    (
        "input_type_error_bool.yml",
        r"""
Error occurred when checking types:
- At user\['some_section'\]\['some_feature'\]:
  Actual \(int\) and declared \(bool\) types do not match""",
    ),
    (
        "input_type_error_float.yml",
        r"""
Error occurred when checking types:
- At user\['some_float'\]:
  Actual \(int\) and declared \(float\) types do not match""",
    ),
    (
        "input_type_error_int.yml",
        r"""
Error occurred when checking types:
- At user\['some_section'\]\['some_number'\]:
  Actual \(float\) and declared \(int\) types do not match""",
    ),
    (
        "input_type_error_list.yml",
        r"""
Error occurred when checking types:
- At user\['some_section'\]\['some_list'\]:
  Actual \(list\) and declared \(List\[float\]\) types do not match""",
    ),
    (
        "input_type_error_str.yml",
        r"""
Error(?:\(s\))? occurred when checking types:
- At user\['some_section'\]\['a_short_string'\]:
  Actual \(int\) and declared \(str\) types do not match""",
    ),
]


@pytest.mark.parametrize(
    "input_file_name,error_message",
    [
        pytest.param(fname, msg, id=fname.rsplit(".", 1)[0])
        for fname, msg in type_checking_data
    ],
)
def test_input_errors(input_file_name, error_message):
    user, template = read_in("input_errors", input_file_name, "template.yml")
    outgoing = merge_ours(theirs=views.view_by_default(template), ours=user)
    types = views.view_by_type(template)

    with pytest.raises(ParselglossyError, match=error_message):
        outgoing = typenade(outgoing, types)
