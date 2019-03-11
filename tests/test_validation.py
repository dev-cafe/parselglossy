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

import os
from pathlib import Path

import pytest

from parselglossy.read_yaml import read_yaml_file
from parselglossy.utils import JSONDict
from parselglossy.validate import (InputError, TemplateError, check_predicates_node, validate_node)


def _helper(category: str, input_file_name: str, template_file_name: str) -> JSONDict:
    this_path = Path(__file__).parent

    input_file = this_path / 'validation' / category / input_file_name
    template_file = this_path / 'validation' / category / template_file_name

    input_dict = read_yaml_file(input_file)
    template_dict = read_yaml_file(template_file)

    # checks everything except predicates
    input_dict = validate_node(input_dict, template_dict)

    # now that all keywords have some value, we can check predicates
    check_predicates_node(input_dict, input_dict, template_dict)

    return input_dict


def test_validation():
    input_dict = _helper('overall', 'input.yml', 'template.yml')

    reference = {
        'title': 'this is an example',
        'scf': {
            'functional': 'B3LYP',
            'max_num_iterations': 20,
            'some_acceleration': True,
            'thresholds': {
                'some_integral_screening': 0.0002,
                'energy': 1e-05
            },
            'another_number': 10,
            # the complex number is a string here because this is how
            # pyyaml interprets it
            # for follow-up please see
            # https://github.com/dev-cafe/parselglossy/issues/26
            'some_complex_number': '0.0+0.0j'
        }
    }

    assert input_dict == reference


def test_template_errors():

    # keyword without doc
    with pytest.raises(TemplateError) as e:
        input_dict = _helper('template_errors', 'input.yml', 'template_no_documentation.yml')
    assert str(e.value) == "keyword(s) without any documentation: ['a_short_string']"

    # keyword with empty doc
    with pytest.raises(TemplateError) as e:
        input_dict = _helper('template_errors', 'input.yml', 'template_empty_documentation.yml')
    assert str(e.value) == "keyword(s) without any documentation: ['a_short_string']"

    # keyword with invalid predicate
    with pytest.raises(TemplateError) as e:
        input_dict = _helper('template_errors', 'input.yml', 'template_invalid_predicate.yml')
    assert str(e.value) == "error in predicate '0 < len(value) <= undefined' in keyword 'a_short_string'"


def test_input_errors():

    # unexpected keyword
    with pytest.raises(InputError) as e:
        input_dict = _helper('input_errors', 'input_unexpected_keyword.yml', 'template.yml')
    assert str(e.value) == "found unexpected keyword(s): {'strange'}"

    # unexpected section
    with pytest.raises(InputError) as e:
        input_dict = _helper('input_errors', 'input_unexpected_section.yml', 'template.yml')
    assert str(e.value) == "found unexpected section(s): {'weird'}"

    # keyword which has not default is not set
    with pytest.raises(InputError) as e:
        input_dict = _helper('input_errors', 'input_missing_keyword.yml', 'template.yml')
    assert str(e.value) == "the following keyword(s) must be set: {'a_short_string'}"

    # type errors
    for file_name, error in [
        ('input_type_error_bool.yml', "incorrect type for keyword: 'some_feature', expected 'bool' type"),
        ('input_type_error_float.yml', "incorrect type for keyword: 'some_float', expected 'float' type"),
        ('input_type_error_int.yml', "incorrect type for keyword: 'some_number', expected 'int' type"),
        ('input_type_error_list.yml', "incorrect type for keyword: 'some_list', expected 'List[float]' type"),
        ('input_type_error_str.yml', "incorrect type for keyword: 'a_short_string', expected 'str' type"),
    ]:
        with pytest.raises(InputError) as e:
            input_dict = _helper('input_errors', file_name, 'template.yml')
        assert str(e.value) == error

    # intra-keyword predicate validation
    with pytest.raises(InputError) as e:
        input_dict = _helper('input_errors', 'input_predicate_intra.yml', 'template.yml')
    assert str(e.value) == 'predicate "value % 2 == 0" failed in keyword "another_number"'

    # predicate validation across keywords
    with pytest.raises(InputError) as e:
        input_dict = _helper('input_errors', 'input_predicate_cross.yml', 'template.yml')
    # in python < 3.6 the dict order is not guaranteed so we are not sure
    # which of the two errors we hit first
    assert str(e.value) in [
        'predicate "value < input_dict[\'some_section\'][\'another_number\']" failed in keyword "some_number"',
        'predicate "value > input_dict[\'some_section\'][\'some_number\']" failed in keyword "another_number"'
    ]
